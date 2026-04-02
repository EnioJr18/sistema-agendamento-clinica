import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import type { Medico } from '../types';

const createDoctor = async (doctor: Omit<Medico, 'id'>): Promise<Medico> => {
  const response = await api.post('/medicos/', doctor);
  return response.data;
};

export const useCreateDoctor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createDoctor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctors'] });
    },
  });
};
