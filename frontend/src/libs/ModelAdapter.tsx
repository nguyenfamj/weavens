import { useRef, type ReactNode } from 'react';
import { graphClient } from './graphClient';
import { useLangGraphRuntime } from '@assistant-ui/react-langgraph';
import { AssistantRuntimeProvider } from '@assistant-ui/react';

export function RuntimeProvider({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const threadIdRef = useRef<string | undefined>();
  const runtime = useLangGraphRuntime({
    threadId: threadIdRef.current,
    stream: async (messages) => {
      if (!threadIdRef.current) {
        const { thread_id } = await graphClient.createThread();
        threadIdRef.current = thread_id;
      }
      const threadId = threadIdRef.current;

      return graphClient.sendMessages({ threadId, messages });
    },
  });

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>;
}
