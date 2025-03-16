import type { LangChainMessage } from '@assistant-ui/react-langgraph';
import { v4 as uuidv4 } from 'uuid';
import { createParser } from './streamUtils/eventParser';
import { IterableReadableStream } from './streamUtils/stream';
import type { EventSourceParser, StreamEvent } from './streamUtils/types';

class GraphClient {
  readonly baseUrl: string = import.meta.env.VITE_LANGGRAPH_API_URL;

  async *sendMessages({
    threadId,
    messages,
  }: {
    threadId: string;
    messages: LangChainMessage[];
  }): AsyncGenerator<{ event: StreamEvent; data: any }> {
    const response = await fetch(`${this.baseUrl}/api/v1/graph/threads/${threadId}/runs/stream`, {
      method: 'POST',
      body: JSON.stringify({ input: { messages } }),
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok || !response.body) {
      throw response.statusText;
    }

    let parser: EventSourceParser;
    let onEndEvent: () => void;
    const textDecoder = new TextDecoder();

    const partialMessages: Map<string, string> = new Map();

    const stream: ReadableStream<{ event: string; data: any }> = (
      response.body || new ReadableStream({ start: (ctrl) => ctrl.close() })
    ).pipeThrough(
      new TransformStream({
        async start(ctrl) {
          parser = createParser((event) => {
            if (event.type === 'event' && event.data === '[DONE]') {
              ctrl.terminate();
              return;
            }

            if ('data' in event) {
              const queueEvent: { event: string; data: unknown } = {
                event: event.event ?? 'message',
                data: {},
              };

              const parsedData: LangChainMessage[] = JSON.parse(event.data);

              if (event.event === 'messages/chunk') {
                const updatedChunk: LangChainMessage[] = [];

                // Add partial messages from with chunk id to the map
                for (const message of parsedData) {
                  if (message.id) {
                    partialMessages.set(
                      message.id,
                      (partialMessages.get(message.id) || '') + message.content
                    );

                    updatedChunk.push({
                      ...message,
                      content: partialMessages.get(message.id) || '',
                    });
                  }
                }

                queueEvent.event = 'messages/partial';
                queueEvent.data = updatedChunk;
              } else {
                queueEvent.data = parsedData;
              }

              ctrl.enqueue(queueEvent);
            }
          });

          onEndEvent = () => {
            ctrl.enqueue({ event: 'end', data: undefined });
          };
        },
        async transform(chunk) {
          const payload = textDecoder.decode(chunk);
          parser.feed(payload);

          if (payload.trim() === 'event: end') onEndEvent();
        },
      })
    );

    yield* IterableReadableStream.fromReadableStream(stream);
  }

  async createThread() {
    return { thread_id: uuidv4() };
  }
}

export const graphClient = new GraphClient();
