import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { Medico } from '../types';

// Função para buscar todos os médicos
const fetchDoctors = async (): Promise<Medico[]> => {
  const response = await api.get('/medicos/');
  return response.data;
};

// Hook para buscar todos os médicos
export const useDoctors = () => {
  return useQuery({
    queryKey: ['doctors'],
    queryFn: fetchDoctors,
  });
};
