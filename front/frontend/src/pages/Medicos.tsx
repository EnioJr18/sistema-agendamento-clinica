import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Card,
  CardContent,
  Avatar,
  Chip,
  Button,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
} from '@mui/material';
import {
  MedicalServices,
  Phone,
  Email,
  Schedule,
  Search,
  CalendarMonth,
} from '@mui/icons-material';
import { mockMedicos } from '../data/mockData';

export default function Medicos() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMedico, setSelectedMedico] = useState<number | null>(null);
  const [openDialog, setOpenDialog] = useState(false);

  const filteredMedicos = mockMedicos.filter(
    medico =>
      medico.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      medico.especialidade.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const handleOpenDialog = (medicoId: number) => {
    setSelectedMedico(medicoId);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedMedico(null);
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
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  const medico = selectedMedico
    ? mockMedicos.find(m => m.id === selectedMedico)
    : null;

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-4"
      >
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
          Nossos Médicos
        </h1>
        <p className="text-base sm:text-lg text-gray-600">
          Conheça nossa equipe de profissionais especializados
        </p>

        {/* Search Bar */}
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Buscar por nome ou especialidade..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          size="medium"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search className="text-gray-400" />
              </InputAdornment>
            ),
          }}
          className="bg-white"
        />
      </motion.div>

      {/* Medicos Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {filteredMedicos.map(medico => (
          <motion.div key={medico.id} variants={itemVariants}>
            <Card className="h-full hover:shadow-2xl transition-shadow duration-300 cursor-pointer">
              <CardContent className="space-y-4 p-4 sm:p-6">
                {/* Avatar e Nome */}
                <div className="flex items-center gap-3 sm:gap-4">
                  <Avatar
                    className="w-16 h-16 bg-linear-to-r from-teal-600 to-cyan-600"
                    sx={{ width: 64, height: 64 }}
                  >
                    <MedicalServices className="text-3xl" />
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-800">
                      {medico.nome}
                    </h3>
                    <Chip
                      label={medico.especialidade}
                      size="small"
                      className="bg-linear-to-r from-teal-100 to-cyan-100 text-teal-700 mt-1"
                    />
                  </div>
                </div>

                {/* Informações */}
                <div className="space-y-2 text-xs sm:text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Email className="text-gray-400 text-base sm:text-lg shrink-0" />
                    <span className="truncate">{medico.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="text-gray-400 text-base sm:text-lg shrink-0" />
                    <span>{medico.telefone}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Schedule className="text-gray-400 text-base sm:text-lg mt-0.5 shrink-0" />
                    <span className="wrap-break-word">
                      {medico.disponibilidade}
                    </span>
                  </div>
                </div>

                {/* CRM */}
                <div className="pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500">CRM: {medico.crm}</p>
                </div>

                {/* Botão de Agendamento */}
                <Button
                  fullWidth
                  variant="contained"
                  size="medium"
                  className="bg-linear-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-sm sm:text-base"
                  startIcon={<CalendarMonth />}
                  onClick={() => handleOpenDialog(medico.id)}
                >
                  Agendar Consulta
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* No Results */}
      {filteredMedicos.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <MedicalServices className="text-6xl text-gray-300 mx-auto mb-4" />
          <p className="text-xl text-gray-500">
            Nenhum médico encontrado com esses critérios
          </p>
        </motion.div>
      )}

      {/* Dialog de Agendamento */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle className="bg-linear-to-r from-teal-600 to-cyan-600 text-white">
          Agendar Consulta
        </DialogTitle>
        <DialogContent className="mt-4 p-4 sm:p-6">
          {medico && (
            <div className="space-y-3 sm:space-y-4">
              <Typography
                variant="h6"
                className="text-gray-800 text-lg sm:text-xl"
              >
                {medico.nome}
              </Typography>
              <Typography variant="body2" className="text-gray-600">
                <strong>Especialidade:</strong> {medico.especialidade}
              </Typography>
              <Typography variant="body2" className="text-gray-600">
                <strong>Disponibilidade:</strong> {medico.disponibilidade}
              </Typography>
              <div className="pt-4">
                <Typography
                  variant="body2"
                  className="text-gray-500 text-center"
                >
                  🚧 Em breve você poderá escolher a data e horário da sua
                  consulta. Esta funcionalidade será integrada com a API.
                </Typography>
              </div>
            </div>
          )}
        </DialogContent>
        <DialogActions className="p-3 sm:p-4 flex-col sm:flex-row gap-2">
          <Button
            onClick={handleCloseDialog}
            className="text-gray-600 w-full sm:w-auto order-2 sm:order-1"
          >
            Fechar
          </Button>
          <Button
            variant="contained"
            className="bg-linear-to-r from-teal-600 to-cyan-600 w-full sm:w-auto order-1 sm:order-2"
            onClick={handleCloseDialog}
          >
            Confirmar (em breve)
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
