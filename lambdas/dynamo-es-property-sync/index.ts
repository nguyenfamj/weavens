import { Client } from '@opensearch-project/opensearch';
import { AwsSigv4Signer } from '@opensearch-project/opensearch/aws';
import { defaultProvider } from '@aws-sdk/credential-provider-node';
import { DynamoDBStreamEvent } from 'aws-lambda';
import { unmarshall } from '@aws-sdk/util-dynamodb';
import type { AttributeValue, StreamRecord } from '@aws-sdk/client-dynamodb-streams';

const AWS_REGION = 'eu-north-1';
const OPENSEARCH_DOMAIN = process.env.OPENSEARCH_DOMAIN;
const PROPERTIES_DYNAMODB_TABLE = 'Properties';
const PROPERTIES_INDEX = 'properties';

if (!OPENSEARCH_DOMAIN) {
  throw new Error('OPENSEARCH_DOMAIN is not set');
}

const client = new Client({
  ...AwsSigv4Signer({
    region: AWS_REGION,
    service: 'es',
    getCredentials: () => {
      const credentialsProvider = defaultProvider();
      return credentialsProvider();
    },
  }),
  node: OPENSEARCH_DOMAIN,
});

export const handler = async (event: DynamoDBStreamEvent): Promise<void> => {
  try {
    const records = event.Records;
    if (!records || records.length === 0) {
      console.log('No records to process, skipping');
      return;
    }

    const promises = records.map(async (record) => {
      // Skip if not an event from the Properties table
      if (!record.eventSourceARN?.includes(`/${PROPERTIES_DYNAMODB_TABLE}`)) {
        return;
      }

      if (!record.dynamodb?.NewImage) {
        return;
      }

      const property = mapImageToSearchFields(
        record.dynamodb.NewImage as Record<string, AttributeValue>
      );

      switch (record.eventName) {
        case 'INSERT':
        case 'MODIFY':
          if (!property.opensearch_version) {
            console.log(`opensearch_version is not set, skip indexing property ${property.id}`);
            break;
          }

          console.log(`Indexing property ${property.id}`);
          await client.index({
            index: PROPERTIES_INDEX,
            id: String(property.id),
            body: property,
          });
          break;
        case 'REMOVE':
          console.log(`Deleting property ${property.id}`);
          await client.delete({
            index: PROPERTIES_INDEX,
            id: String(property.id),
          });
          break;
      }
    });

    await Promise.all(promises);
    console.log(`Successfully processed ${event.Records.length} records`);
  } catch (error) {
    console.error('Error processing DynamoDB stream records', error);
    throw error;
  }
};

export const mapImageToSearchFields = (image: StreamRecord['NewImage']): Property => {
  const unmarshalledImage = unmarshall(image as Record<string, AttributeValue>) as Property;

  delete unmarshalledImage.image_urls;
  delete unmarshalledImage.has_energy_certificate;
  delete unmarshalledImage.energy_class;
  delete unmarshalledImage.heating;
  delete unmarshalledImage.future_renovations;
  delete unmarshalledImage.completed_renovations;

  return unmarshalledImage;
};
