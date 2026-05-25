// Feature barrel: export everything the chat feature exposes to the rest of the app.
// Add more exports here as the feature grows.
export { default as ChatWindow } from "@/components/chat/ChatWindow";
export { default as ChatInput } from "@/components/chat/ChatInput";
export { default as MessageBubble } from "@/components/chat/MessageBubble";
export { useChat } from "@/hooks/useChat";
