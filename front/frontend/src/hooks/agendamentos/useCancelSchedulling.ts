import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import type { Agendamento } from '../../types';

const cancelSchedulling = async (id: number): Promise<Agendamento> => {
  const response = await api.patch(`/agendamentos/${id}/`, {
    status: 'CANCELADO',
  });
  return response.data;
};

export const useCancelSchedulling = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: cancelSchedulling,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedullings'] });
    },
  });
};
