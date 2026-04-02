import { useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';
import type { AuthTokens, LoginCredentials } from '../../types';

const loginUser = async (
  credentials: LoginCredentials,
): Promise<AuthTokens> => {
  const response = await api.post('/token/', credentials);
  return response.data;
};

export const useCreateUser = () => {
  return useMutation({
    mutationFn: loginUser,
    onSuccess: (tokens, credentials) => {
      localStorage.setItem('token', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      localStorage.setItem('username', credentials.username);
      const existingDisplayName = localStorage
        .getItem('authDisplayName')
        ?.trim();
      if (!existingDisplayName) {
        localStorage.setItem('authDisplayName', credentials.username);
      }
    },
  });
};
