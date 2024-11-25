import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Message {
  from: 'user' | 'bot';
  text: string;
  id: number;
}

interface Chat {
  chatId: string;
  messages: Message[];
}

interface ChatState {
  chats: Chat[];
  responses: { [key: number]: string };
  loading: boolean;
}

const initialState: ChatState = {
  chats: [],
  responses: {},
  loading: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<{ chatId: string; message: Message }>) => {
      const chat = state.chats.find(c => c.chatId === action.payload.chatId);
      if (chat) {
        chat.messages.push(action.payload.message);
      }
    },
    setResponse: (state, action: PayloadAction<{ id: number; response: string }>) => {
      state.responses[action.payload.id] = action.payload.response;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    addChat: (state, action: PayloadAction<{ chatId: string }>) => {
      state.chats.push({ chatId: action.payload.chatId, messages: [] });
    },
  },
});

export const { addMessage, setResponse, setLoading, addChat } = chatSlice.actions;
export default chatSlice.reducer;
