import ChatWindow from "@/components/chat/ChatWindow";

interface Props {
  params: Promise<{ sessionId: string }>;
}

export default async function ChatPage({ params }: Props) {
  const { sessionId } = await params;
  return (
    <main className="flex h-screen flex-col">
      <ChatWindow sessionId={sessionId} />
    </main>
  );
}
