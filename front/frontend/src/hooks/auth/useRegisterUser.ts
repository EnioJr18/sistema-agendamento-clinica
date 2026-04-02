import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import type { RegisterUserData, Usuario } from '../../types';

const registerUser = async (user: RegisterUserData): Promise<Usuario> => {
  const response = await api.post('/usuarios/', user);
  return response.data;
};

export const useRegisterUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: registerUser,
    onSuccess: user => {
      const displayName = user.first_name?.trim() || user.username?.trim();
      if (displayName) {
        localStorage.setItem('authDisplayName', displayName);
      }
      if (user.username?.trim()) {
        localStorage.setItem('username', user.username.trim());
      }
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
