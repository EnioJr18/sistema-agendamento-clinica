import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import type { Agendamento, CreateSchedullingData } from '../../types';

const createSchedulling = async (
  payload: CreateSchedullingData,
): Promise<Agendamento> => {
  const response = await api.post('/agendamentos/', payload);
  return response.data;
};

export const useCreateSchedulling = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createSchedulling,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedullings'] });
    },
  });
};
