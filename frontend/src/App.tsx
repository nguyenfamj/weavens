import { Thread } from '@assistant-ui/react';
import './App.css';
import { RuntimeProvider } from './libs/ModelAdapter';
import { makeMarkdownText } from '@assistant-ui/react-markdown';

const MarkdownText = makeMarkdownText();

function App() {
  return (
    <div className='font-montserrat h-dvh'>
      <RuntimeProvider>
        <div className='flex h-full flex-col'>
          <Thread
            assistantAvatar={{
              src: 'https://assets.science.nasa.gov/dynamicimage/assets/science/psd/solar/2023/07/titan_carousel2.jpg?w=4096&format=jpeg&fit=clip&crop=faces%2Cfocalpoint',
            }}
            welcome={{
              message:
                'Welcome to Weavens, a powerful AI assistant for finding apartment in Finland.',
              suggestions: [
                {
                  prompt: 'Can you help me find a 2 rooms apartment in Espoo, Finland?',
                },
                {
                  prompt: 'Can you help me find an apartment in Malmi, Helsinki for single person?',
                },
              ],
            }}
            assistantMessage={{ components: { Text: MarkdownText } }}
          />
        </div>
      </RuntimeProvider>
    </div>
  );
}

export default App;
