import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import {
  AccountCircle,
  Badge,
  CalendarMonth,
  Email,
  Lock,
  Phone,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import type { RegisterUserData, Usuario } from '../../types';
import { useCreateUser } from '../../hooks/auth/useCreateUser';
import { useRegisterUser } from '../../hooks/auth/useRegisterUser';

function getErrorMessage(error: unknown): string {
  const maybeAxios = error as {
    response?: { data?: unknown; status?: number };
    message?: string;
  };

  const data = maybeAxios?.response?.data;
  if (typeof data === 'string' && data.trim()) return data;

  if (data && typeof data === 'object') {
    // Common DRF patterns: {detail: "..."} or {field: ["..."]}
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) return detail;

    const firstKey = Object.keys(data as Record<string, unknown>)[0];
    const firstVal = (data as Record<string, unknown>)[firstKey];
    if (typeof firstVal === 'string' && firstVal.trim()) return firstVal;
    if (Array.isArray(firstVal) && typeof firstVal[0] === 'string') {
      return firstVal[0];
    }
  }

  if (typeof maybeAxios?.message === 'string' && maybeAxios.message.trim()) {
    return maybeAxios.message;
  }

  return 'Ocorreu um erro inesperado. Tente novamente.';
}

type Mode = 'login' | 'register';

export default function AuthCard() {
  const [searchParams] = useSearchParams();
  const urlMode = searchParams.get('mode');

  const loginMutation = useCreateUser();
  const registerMutation = useRegisterUser();

  const [mode, setMode] = useState<Mode>(() =>
    urlMode === 'register' ? 'register' : 'login',
  );
  const [showPassword, setShowPassword] = useState(false);

  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  });

  const [registerForm, setRegisterForm] = useState<RegisterUserData>({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    tipo: 'PACIENTE',
    telefone: '',
    data_nascimento: null,
  });

  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fieldSx = {
    '& .MuiOutlinedInput-root': {
      borderRadius: '14px',
      backgroundColor: '#ffffff',
      transition: 'all 0.2s ease',
      '&:hover': {
        backgroundColor: '#ffffff',
      },
      '&.Mui-focused': {
        boxShadow: '0 0 0 4px rgba(13, 148, 136, 0.12)',
      },
    },
    '& .MuiInputLabel-root': {
      backgroundColor: '#ffffff',
      paddingLeft: '4px',
      paddingRight: '4px',
    },
  } as const;

  const selectSx = {
    '& .MuiOutlinedInput-root': {
      borderRadius: '14px',
      backgroundColor: '#ffffff',
      '&.Mui-focused': {
        boxShadow: '0 0 0 4px rgba(13, 148, 136, 0.12)',
      },
    },
    '& .MuiInputLabel-root': {
      backgroundColor: '#ffffff',
      paddingLeft: '4px',
      paddingRight: '4px',
    },
  } as const;

  const isBusy = loginMutation.isPending || registerMutation.isPending;

  const loginError = useMemo(() => {
    if (!loginMutation.error) return null;
    return getErrorMessage(loginMutation.error);
  }, [loginMutation.error]);

  const registerError = useMemo(() => {
    if (!registerMutation.error) return null;
    return getErrorMessage(registerMutation.error);
  }, [registerMutation.error]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setSuccessMessage(null);
    setMode(newValue === 0 ? 'login' : 'register');
  };

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();
    setSuccessMessage(null);

    if (!loginForm.username.trim() || !loginForm.password) return;

    loginMutation.mutate(
      {
        username: loginForm.username.trim(),
        password: loginForm.password,
      },
      {
        onSuccess: () => {
          window.location.href = '/';
        },
      },
    );
  };

  const handleRegister = (event: React.FormEvent) => {
    event.preventDefault();
    setSuccessMessage(null);

    const payload: RegisterUserData = {
      ...registerForm,
      username: registerForm.username.trim(),
      first_name: registerForm.first_name.trim(),
      last_name: registerForm.last_name.trim(),
      email: registerForm.email.trim(),
      telefone: registerForm.telefone?.trim() || null,
      data_nascimento: registerForm.data_nascimento || null,
    };

    if (
      !payload.username ||
      !payload.first_name ||
      !payload.last_name ||
      !payload.email ||
      !payload.password
    ) {
      return;
    }

    registerMutation.mutate(payload, {
      onSuccess: (user: Usuario) => {
        setSuccessMessage(
          `Conta criada com sucesso para ${user.first_name}. Agora é só entrar!`,
        );
        setMode('login');
        setLoginForm(prev => ({ ...prev, username: payload.username }));
      },
    });
  };

  const activeTab = mode === 'login' ? 0 : 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <Card className="overflow-hidden border border-teal-100/80 shadow-2xl shadow-teal-100/50 backdrop-blur-sm">
        <div className="bg-linear-to-r from-teal-700 via-teal-600 to-cyan-600 p-6 text-white">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <Typography
                variant="h5"
                className="font-extrabold tracking-tight"
              >
                Acesse sua conta
              </Typography>
              <Typography variant="body2" className="opacity-90">
                Faça login ou crie um cadastro para agendar consultas.
              </Typography>
            </div>
            <Chip
              label="CLINAB"
              className="bg-white/20 text-white border border-white/30"
              variant="outlined"
            />
          </div>
        </div>

        <Box className="bg-white">
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            TabIndicatorProps={{
              style: {
                background: 'linear-gradient(to right, #0d9488, #06b6d4)',
              },
            }}
            className="border-b border-gray-200"
          >
            <Tab label="Entrar" className="min-h-14" />
            <Tab label="Criar conta" className="min-h-14" />
          </Tabs>
        </Box>

        <CardContent className="bg-slate-50/50 p-6 sm:p-8">
          <div className="space-y-4">
            {successMessage && (
              <Alert severity="success" onClose={() => setSuccessMessage(null)}>
                {successMessage}
              </Alert>
            )}

            <AnimatePresence mode="wait" initial={false}>
              {mode === 'login' ? (
                <motion.div
                  key="login"
                  initial={{ opacity: 0, x: -18 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 18 }}
                  transition={{ duration: 0.24, ease: 'easeOut' }}
                  className="space-y-4"
                >
                  {loginError && <Alert severity="error">{loginError}</Alert>}

                  <form onSubmit={handleLogin} className="space-y-4">
                    <TextField
                      label="Usuário"
                      value={loginForm.username}
                      onChange={e =>
                        setLoginForm(prev => ({
                          ...prev,
                          username: e.target.value,
                        }))
                      }
                      fullWidth
                      variant="outlined"
                      size="small"
                      autoComplete="username"
                      disabled={isBusy}
                      sx={fieldSx}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <AccountCircle className="text-gray-400" />
                          </InputAdornment>
                        ),
                      }}
                    />

                    <TextField
                      label="Senha"
                      value={loginForm.password}
                      onChange={e =>
                        setLoginForm(prev => ({
                          ...prev,
                          password: e.target.value,
                        }))
                      }
                      type={showPassword ? 'text' : 'password'}
                      fullWidth
                      variant="outlined"
                      size="small"
                      autoComplete="current-password"
                      disabled={isBusy}
                      sx={fieldSx}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Lock className="text-gray-400" />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(v => !v)}
                              edge="end"
                              aria-label={
                                showPassword ? 'ocultar senha' : 'mostrar senha'
                              }
                              disabled={isBusy}
                            >
                              {showPassword ? (
                                <VisibilityOff />
                              ) : (
                                <Visibility />
                              )}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />

                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      fullWidth
                      disabled={
                        isBusy ||
                        !loginForm.username.trim() ||
                        !loginForm.password
                      }
                      className="bg-linear-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 py-3"
                    >
                      {loginMutation.isPending ? 'Entrando...' : 'Entrar'}
                    </Button>

                    <Divider className="my-4!" />

                    <div className="text-center">
                      <Typography variant="body2" className="text-gray-600">
                        Não tem conta?{' '}
                        <button
                          type="button"
                          onClick={() => setMode('register')}
                          className="text-teal-700 font-semibold hover:underline"
                          disabled={isBusy}
                        >
                          Cadastre-se
                        </button>
                      </Typography>
                    </div>
                  </form>
                </motion.div>
              ) : (
                <motion.div
                  key="register"
                  initial={{ opacity: 0, x: 18 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -18 }}
                  transition={{ duration: 0.24, ease: 'easeOut' }}
                  className="space-y-4"
                >
                  {registerError && (
                    <Alert severity="error">{registerError}</Alert>
                  )}

                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <TextField
                        label="Nome"
                        value={registerForm.first_name}
                        onChange={e =>
                          setRegisterForm(prev => ({
                            ...prev,
                            first_name: e.target.value,
                          }))
                        }
                        fullWidth
                        variant="outlined"
                        size="small"
                        disabled={isBusy}
                        autoComplete="given-name"
                        sx={fieldSx}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Badge className="text-gray-400" />
                            </InputAdornment>
                          ),
                        }}
                      />

                      <TextField
                        label="Sobrenome"
                        value={registerForm.last_name}
                        onChange={e =>
                          setRegisterForm(prev => ({
                            ...prev,
                            last_name: e.target.value,
                          }))
                        }
                        fullWidth
                        variant="outlined"
                        size="small"
                        disabled={isBusy}
                        autoComplete="family-name"
                        sx={fieldSx}
                      />
                    </div>

                    <TextField
                      label="Usuário"
                      value={registerForm.username}
                      onChange={e =>
                        setRegisterForm(prev => ({
                          ...prev,
                          username: e.target.value,
                        }))
                      }
                      fullWidth
                      variant="outlined"
                      size="small"
                      disabled={isBusy}
                      autoComplete="username"
                      sx={fieldSx}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <AccountCircle className="text-gray-400" />
                          </InputAdornment>
                        ),
                      }}
                    />

                    <TextField
                      label="Email"
                      value={registerForm.email}
                      onChange={e =>
                        setRegisterForm(prev => ({
                          ...prev,
                          email: e.target.value,
                        }))
                      }
                      fullWidth
                      variant="outlined"
                      size="small"
                      disabled={isBusy}
                      autoComplete="email"
                      sx={fieldSx}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Email className="text-gray-400" />
                          </InputAdornment>
                        ),
                      }}
                    />

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormControl
                        fullWidth
                        disabled={isBusy}
                        size="small"
                        sx={selectSx}
                      >
                        <InputLabel id="tipo-label">Tipo</InputLabel>
                        <Select
                          labelId="tipo-label"
                          label="Tipo"
                          value={registerForm.tipo || 'PACIENTE'}
                          onChange={e =>
                            setRegisterForm(prev => ({
                              ...prev,
                              tipo: e.target.value as RegisterUserData['tipo'],
                            }))
                          }
                        >
                          <MenuItem value="PACIENTE">Paciente</MenuItem>
                          <MenuItem value="MEDICO">Médico</MenuItem>
                        </Select>
                      </FormControl>

                      <TextField
                        label="Telefone (opcional)"
                        value={registerForm.telefone || ''}
                        onChange={e =>
                          setRegisterForm(prev => ({
                            ...prev,
                            telefone: e.target.value,
                          }))
                        }
                        fullWidth
                        variant="outlined"
                        size="small"
                        disabled={isBusy}
                        autoComplete="tel"
                        sx={fieldSx}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Phone className="text-gray-400" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <TextField
                        label="Data de nascimento (opcional)"
                        type="date"
                        value={registerForm.data_nascimento || ''}
                        onChange={e =>
                          setRegisterForm(prev => ({
                            ...prev,
                            data_nascimento: e.target.value || null,
                          }))
                        }
                        fullWidth
                        variant="outlined"
                        size="small"
                        disabled={isBusy}
                        InputLabelProps={{ shrink: true }}
                        sx={fieldSx}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <CalendarMonth className="text-gray-400" />
                            </InputAdornment>
                          ),
                        }}
                      />

                      <TextField
                        label="Senha"
                        value={registerForm.password}
                        onChange={e =>
                          setRegisterForm(prev => ({
                            ...prev,
                            password: e.target.value,
                          }))
                        }
                        type={showPassword ? 'text' : 'password'}
                        fullWidth
                        variant="outlined"
                        size="small"
                        disabled={isBusy}
                        autoComplete="new-password"
                        sx={fieldSx}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock className="text-gray-400" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowPassword(v => !v)}
                                edge="end"
                                aria-label={
                                  showPassword
                                    ? 'ocultar senha'
                                    : 'mostrar senha'
                                }
                                disabled={isBusy}
                              >
                                {showPassword ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </div>

                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      fullWidth
                      disabled={
                        isBusy ||
                        !registerForm.username.trim() ||
                        !registerForm.first_name.trim() ||
                        !registerForm.last_name.trim() ||
                        !registerForm.email.trim() ||
                        !registerForm.password
                      }
                      className="bg-linear-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 py-3"
                    >
                      {registerMutation.isPending
                        ? 'Criando conta...'
                        : 'Criar conta'}
                    </Button>

                    <Divider className="my-4!" />

                    <div className="text-center">
                      <Typography variant="body2" className="text-gray-600">
                        Já tem conta?{' '}
                        <button
                          type="button"
                          onClick={() => setMode('login')}
                          className="text-teal-700 font-semibold hover:underline"
                          disabled={isBusy}
                        >
                          Entrar
                        </button>
                      </Typography>
                    </div>
                  </form>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
