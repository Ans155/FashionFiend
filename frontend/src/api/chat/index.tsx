import { getCookies, handleStoreCookie, removeAllCookies } from '../../helpers/storage';

const BASE_URL = 'http://127.0.0.1:8000';
// const BASE_URL = 'http://localhost:5000';

export const refreshAccessToken = async (): Promise<string> => {
  const refreshToken = getCookies('refreshToken') || '';
  if (!refreshToken) throw new Error('No refresh token available');

  try {
    const response = await fetch(`${BASE_URL}/auth/token/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refreshToken }),
    });
    const data = await response.json();
    if (response.ok) {
      const { access_token, refresh_token } = data?.data || {};
      handleStoreCookie(access_token, refresh_token);
      return access_token;
    } else {
      throw new Error(data?.message || 'Failed to refresh token');
    }
  } catch (error) {
    console.error('Error refreshing access token:', error);
    removeAllCookies();
    window.location.reload();
    throw error;
  }
};

export const isTokenExpired = (): boolean => {
  const tokenExpirationTime = getCookies('tokenExpirationTime');
  if (!tokenExpirationTime) return true;
  return new Date().getTime() > Number(tokenExpirationTime);
};

export const sendMessageToAPI = async (question: string, messageId?: number) => {
  try {

    const response = await fetch(`${BASE_URL}/recommendations`, {
      method: 'POST',
      headers: {
        Accept: "application/json",
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query:question }),
    });
    const data = await response.json();
    console.log(data)
    return { answer: data, messageId };
  } catch (error) {
    return { answer: 'Sorry, something went wrong. Please try again later.', messageId };
  }
};

export const addMessageToConversation = async (chatId: string, message: any, role: 'user' | 'ai') => {
  let accessToken = getCookies('accessToken');

    if (isTokenExpired()) {
      accessToken = await refreshAccessToken();
    }
  const response = await fetch(`${BASE_URL}/p/bpx/conversations/add/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken ? `Bearer ${accessToken}` : '',
    },
    body: JSON.stringify({
      conversation_id: chatId,
      content: {
        message: message.text,
      },
      role,
      feedback: {
        upvote: false,
        downvote: false,
        text: '',
      },
    }),
  });
  if (!response.ok) {
    throw new Error('Failed to add message');
  }
  return response.json();
};


// Get Messages from Conversation API
export const getMessagesFromConversation = async (conversationId: string) => {
  let accessToken = getCookies('accessToken');

    if (isTokenExpired()) {
      accessToken = await refreshAccessToken();
    }
  const response = await fetch(`${BASE_URL}/p/bpx/conversations/${conversationId}/messages`,{
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken ? `Bearer ${accessToken}` : '',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
};

export const createConversation = async (userId: string, name: string) => {
  let accessToken = getCookies('accessToken');

    if (isTokenExpired()) {
      accessToken = await refreshAccessToken();
    }
  try {
    const response = await fetch(`${BASE_URL}/p/bpx/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': accessToken ? `Bearer ${accessToken}` : '',
      },
      body: JSON.stringify({ user_id:userId, name }),
    });
    return await response.json();
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
};
export const getAllConversation = async (userId: string) => {
  let accessToken = getCookies('accessToken');

    if (isTokenExpired()) {
      accessToken = await refreshAccessToken();
    }
  const response = await fetch(`${BASE_URL}/p/bpx/conversations/user/${userId}`,{
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken ? `Bearer ${accessToken}` : '',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
};
export const deleteConversation = async (conversationId: string) => {
  let accessToken = getCookies('accessToken');

    if (isTokenExpired()) {
      accessToken = await refreshAccessToken();
    }
  const response = await fetch(`${BASE_URL}/p/bpx/conversations/${conversationId}`,{
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken ? `Bearer ${accessToken}` : '',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
};

export const criticAPI = async (
  conversationId: string, 
  messageId: string, 
  feedback: { upvote: boolean; downvote: boolean; text: string }
) => {
  let accessToken = getCookies('accessToken');

  if (isTokenExpired()) {
    accessToken = await refreshAccessToken();
  }

  try {
    const response = await fetch(`${BASE_URL}/p/bpx/conversations/${conversationId}/messages/${messageId}`, {
      method: 'PUT', 
      headers: {
        'Content-Type': 'application/json',
        'Authorization': accessToken ? `Bearer ${accessToken}` : '',
      },
      body: JSON.stringify({
        feedback: feedback,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to update the message');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating message:', error);
    throw error;
  }
};
