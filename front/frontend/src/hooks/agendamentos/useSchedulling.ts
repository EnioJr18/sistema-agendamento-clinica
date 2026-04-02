import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import type { Agendamento } from '../../types';

const fetchSchedullings = async (): Promise<Agendamento[]> => {
  const response = await api.get('/agendamentos/');
  return response.data;
};

export const useSchedulling = () => {
  return useQuery({
    queryKey: ['schedullings'],
    queryFn: fetchSchedullings,
  });
};
