import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Alert,
  Card,
  CardContent,
  Chip,
  Button,
  Tabs,
  Tab,
  Box,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
} from '@mui/material';
import {
  CalendarMonth,
  Schedule,
  CheckCircle,
  Cancel,
  Info,
  Delete,
} from '@mui/icons-material';
import type { Agendamento } from '../types';
import { useSchedulling } from '../hooks/agendamentos/useSchedulling';
import { useCancelSchedulling } from '../hooks/agendamentos/useCancelSchedulling';

export default function Agendamentos() {
  const [tabValue, setTabValue] = useState(0);
  const [selectedAgendamento, setSelectedAgendamento] =
    useState<Agendamento | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [confirmCancelOpen, setConfirmCancelOpen] = useState(false);
  const [pendingCancelId, setPendingCancelId] = useState<number | null>(null);

  const { data: schedullings = [], isLoading, isError } = useSchedulling();
  const cancelSchedullingMutation = useCancelSchedulling();

  // Filtra agendamentos com base na aba selecionada
  const filteredAgendamentos = useMemo(() => {
    switch (tabValue) {
      case 0: // Próximos
        return schedullings.filter(
          a => a.status === 'AGENDADO' && new Date(a.data_horario) > new Date(),
        );
      case 1: // Histórico
        return schedullings.filter(
          a =>
            a.status === 'CONCLUIDO' || new Date(a.data_horario) < new Date(),
        );
      case 2: // Cancelados
        return schedullings.filter(a => a.status === 'CANCELADO');
      default:
        return schedullings;
    }
  }, [tabValue, schedullings]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (agendamento: Agendamento) => {
    setSelectedAgendamento(agendamento);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedAgendamento(null);
    cancelSchedullingMutation.reset();
  };

  const handleOpenCancelConfirm = (agendamentoId: number) => {
    setPendingCancelId(agendamentoId);
    setConfirmCancelOpen(true);
  };

  const handleCloseCancelConfirm = () => {
    setConfirmCancelOpen(false);
    setPendingCancelId(null);
  };

  const handleCancelSchedulling = (agendamentoId: number) => {
    cancelSchedullingMutation.mutate(agendamentoId, {
      onSuccess: () => {
        handleCloseCancelConfirm();
        if (selectedAgendamento?.id === agendamentoId) {
          handleCloseDialog();
        }
      },
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AGENDADO':
        return 'bg-blue-100 text-blue-700';
      case 'CONCLUIDO':
        return 'bg-green-100 text-green-700';
      case 'CANCELADO':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'AGENDADO':
        return <Schedule className="text-blue-600" />;
      case 'CONCLUIDO':
        return <CheckCircle className="text-green-600" />;
      case 'CANCELADO':
        return <Cancel className="text-red-600" />;
      default:
        return <Info className="text-gray-600" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.4,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
          Meus Agendamentos
        </h1>
        <p className="text-gray-600">Carregando agendamentos...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
          Meus Agendamentos
        </h1>
        <p className="text-red-600">
          Não foi possível carregar os agendamentos. Tente novamente.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-4"
      >
        <h1 className="text-4xl md:text-5xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
          Meus Agendamentos
        </h1>
        <p className="text-lg text-gray-600">
          Gerencie suas consultas e acompanhe seu histórico
        </p>
      </motion.div>

      {/* Tabs */}
      <Box className="bg-white rounded-lg shadow-sm">
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          className="border-b border-gray-200"
          variant="scrollable"
          scrollButtons="auto"
          TabIndicatorProps={{
            style: {
              background: 'linear-gradient(to right, #0d9488, #06b6d4)',
            },
          }}
        >
          <Tab
            label="Próximos"
            icon={<Schedule />}
            iconPosition="start"
            className="min-h-16 text-sm sm:text-base"
          />
          <Tab
            label="Histórico"
            icon={<CheckCircle />}
            iconPosition="start"
            className="min-h-16 text-sm sm:text-base"
          />
          <Tab
            label="Cancelados"
            icon={<Cancel />}
            iconPosition="start"
            className="min-h-16 text-sm sm:text-base"
          />
        </Tabs>
      </Box>

      {/* Agendamentos List */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {cancelSchedullingMutation.isError && (
          <Alert severity="error">
            Nao foi possivel cancelar o agendamento. Tente novamente.
          </Alert>
        )}

        {filteredAgendamentos.length > 0 ? (
          filteredAgendamentos.map(agendamento => (
            <motion.div key={agendamento.id} variants={itemVariants}>
              <Card className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* Informações do Agendamento */}
                    <div className="flex-1 space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="mt-1">
                          {getStatusIcon(agendamento.status)}
                        </div>
                        <div className="flex-1">
                          <h3 className="text-xl font-semibold text-gray-800">
                            {agendamento.nome_medico}
                          </h3>
                          <p className="text-gray-600">
                            {agendamento.especialidade_medico}
                          </p>
                        </div>
                        <Chip
                          label={agendamento.status}
                          size="small"
                          className={getStatusColor(agendamento.status)}
                        />
                      </div>

                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <CalendarMonth className="text-gray-400" />
                          <span>{formatDate(agendamento.data_horario)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Schedule className="text-gray-400" />
                          <span>{formatTime(agendamento.data_horario)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Ações */}
                    <div className="flex flex-col sm:flex-row gap-2">
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Info />}
                        onClick={() => handleOpenDialog(agendamento)}
                        className="border-teal-600 text-teal-600 hover:bg-teal-50 w-full sm:w-auto"
                      >
                        Detalhes
                      </Button>
                      {agendamento.status === 'AGENDADO' && (
                        <IconButton
                          size="small"
                          className="text-red-600 hover:bg-red-50 self-center sm:self-auto"
                          title="Cancelar"
                          onClick={() =>
                            handleOpenCancelConfirm(agendamento.id)
                          }
                          disabled={cancelSchedullingMutation.isPending}
                        >
                          <Delete />
                        </IconButton>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 bg-white rounded-lg shadow-sm"
          >
            <CalendarMonth className="text-6xl text-gray-300 mx-auto mb-4" />
            <p className="text-xl text-gray-500">
              Nenhum agendamento encontrado nesta categoria
            </p>
          </motion.div>
        )}
      </motion.div>

      {/* Dialog de Detalhes */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle className="bg-linear-to-r from-teal-600 to-cyan-600 text-white">
          Detalhes do Agendamento
        </DialogTitle>
        <DialogContent className="mt-4">
          {selectedAgendamento && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Typography variant="h6" className="text-gray-800">
                  {selectedAgendamento.nome_medico}
                </Typography>
                <Chip
                  label={selectedAgendamento.status}
                  className={getStatusColor(selectedAgendamento.status)}
                />
              </div>

              <div className="space-y-2 text-gray-600">
                <Typography variant="body1">
                  <strong>Especialidade:</strong>{' '}
                  {selectedAgendamento.especialidade_medico}
                </Typography>
                <Typography variant="body1">
                  <strong>Data:</strong>{' '}
                  {formatDate(selectedAgendamento.data_horario)}
                </Typography>
                <Typography variant="body1">
                  <strong>Horário:</strong>{' '}
                  {formatTime(selectedAgendamento.data_horario)}
                </Typography>
                <Typography variant="body2" className="text-gray-500 pt-2">
                  Agendado em:{' '}
                  {new Date(selectedAgendamento.criado_em).toLocaleString(
                    'pt-BR',
                  )}
                </Typography>
              </div>

              {selectedAgendamento.status === 'AGENDADO' && (
                <div className="pt-4 border-t border-gray-200">
                  <Typography variant="body2" className="text-gray-600">
                    💡 Chegue com 15 minutos de antecedência e traga seus exames
                    anteriores, se tiver.
                  </Typography>
                </div>
              )}
            </div>
          )}
        </DialogContent>
        <DialogActions className="p-4 flex-col sm:flex-row gap-2">
          <Button
            onClick={handleCloseDialog}
            className="text-gray-600 w-full sm:w-auto order-2 sm:order-1"
          >
            Fechar
          </Button>
          {selectedAgendamento?.status === 'AGENDADO' && (
            <Button
              variant="outlined"
              color="error"
              onClick={() => handleOpenCancelConfirm(selectedAgendamento.id)}
              disabled={cancelSchedullingMutation.isPending}
              className="w-full sm:w-auto order-1 sm:order-2"
            >
              {cancelSchedullingMutation.isPending
                ? 'Cancelando...'
                : 'Cancelar Consulta'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      <Dialog
        open={confirmCancelOpen}
        onClose={handleCloseCancelConfirm}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle className="text-red-600">
          Confirmar cancelamento
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" className="text-gray-700">
            Tem certeza que deseja cancelar este agendamento?
          </Typography>
        </DialogContent>
        <DialogActions className="p-4 gap-2">
          <Button
            onClick={handleCloseCancelConfirm}
            disabled={cancelSchedullingMutation.isPending}
          >
            Voltar
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={() =>
              pendingCancelId && handleCancelSchedulling(pendingCancelId)
            }
            disabled={!pendingCancelId || cancelSchedullingMutation.isPending}
          >
            {cancelSchedullingMutation.isPending
              ? 'Cancelando...'
              : 'Confirmar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* CTA Section - Novo Agendamento */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="bg-linear-to-r from-teal-600 to-cyan-600 text-white rounded-2xl p-6 sm:p-8 text-center space-y-4"
      >
        <h3 className="text-xl sm:text-2xl font-bold">
          Precisa agendar uma consulta?
        </h3>
        <p className="text-base sm:text-lg opacity-90">
          Escolha um de nossos especialistas e marque seu horário
        </p>
        <Button
          variant="contained"
          size="large"
          className="bg-white text-teal-600 hover:bg-gray-100 px-6 sm:px-8 py-3 w-full sm:w-auto"
          startIcon={<CalendarMonth />}
        >
          Ver Médicos Disponíveis
        </Button>
      </motion.div>
    </div>
  );
}
