import { motion } from 'framer-motion';
import { Card, CardContent, Button, Container } from '@mui/material';
import {
  CalendarMonth,
  MedicalServices,
  Favorite,
  Psychology,
  Healing,
  HealthAndSafety,
} from '@mui/icons-material';

export default function Home() {
  const services = [
    {
      icon: <MedicalServices className="text-5xl" />,
      title: 'Consultas Gerais',
      description: 'Atendimento médico completo e personalizado',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: <Favorite className="text-5xl" />,
      title: 'Cardiologia',
      description: 'Cuidados especializados para seu coração',
      color: 'from-red-500 to-red-600',
    },
    {
      icon: <Psychology className="text-5xl" />,
      title: 'Neurologia',
      description: 'Tratamento especializado do sistema nervoso',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: <Healing className="text-5xl" />,
      title: 'Ortopedia',
      description: 'Tratamento de lesões e doenças ósseas',
      color: 'from-green-500 to-green-600',
    },
    {
      icon: <HealthAndSafety className="text-5xl" />,
      title: 'Pediatria',
      description: 'Cuidados especiais para as crianças',
      color: 'from-yellow-500 to-yellow-600',
    },
    {
      icon: <CalendarMonth className="text-5xl" />,
      title: 'Agendamento Online',
      description: 'Agende sua consulta de forma rápida e fácil',
      color: 'from-teal-500 to-teal-600',
    },
  ];

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

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center space-y-6 py-12"
      >
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold bg-linear-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
            Bem-vindo à CLINAB
          </h1>
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto"
        >
          Sua saúde é nossa prioridade. Oferecemos atendimento médico de
          excelência com profissionais qualificados e tecnologia de ponta.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4"
        >
          <Button
            variant="contained"
            size="large"
            className="bg-linear-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 px-8 py-3 text-lg"
            startIcon={<CalendarMonth />}
          >
            Agendar Consulta
          </Button>
          <Button
            variant="outlined"
            size="large"
            className="border-2 border-teal-600 text-teal-600 hover:bg-teal-50 px-8 py-3 text-lg"
          >
            Conhecer Médicos
          </Button>
        </motion.div>
      </motion.section>

      {/* Services Section */}
      <Container maxWidth="lg">
        <motion.section
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="space-y-8"
        >
          <motion.div variants={itemVariants} className="text-center">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Nossos Serviços
            </h2>
            <p className="text-lg text-gray-600">
              Oferecemos uma ampla gama de especialidades médicas
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
              >
                <Card className="h-full hover:shadow-2xl transition-shadow duration-300 cursor-pointer">
                  <CardContent className="text-center space-y-4 p-6">
                    <div
                      className={`w-20 h-20 mx-auto rounded-full bg-linear-to-r ${service.color} flex items-center justify-center text-white shadow-lg`}
                    >
                      {service.icon}
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800">
                      {service.title}
                    </h3>
                    <p className="text-gray-600">{service.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </Container>

      {/* CTA Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="bg-linear-to-r from-teal-600 to-cyan-600 text-white rounded-2xl p-12 text-center space-y-6 shadow-xl"
      >
        <h2 className="text-3xl md:text-4xl font-bold">
          Pronto para cuidar da sua saúde?
        </h2>
        <p className="text-xl opacity-90">
          Agende sua consulta agora e receba atendimento de qualidade
        </p>
        <Button
          variant="contained"
          size="large"
          className="bg-white text-teal-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold"
        >
          Falar com a Recepção
        </Button>
      </motion.section>
    </div>
  );
}
