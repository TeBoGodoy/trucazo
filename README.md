# Marcaciones Automáticas

Script automatizado para enviar marcaciones de entrada/salida a IzyTimeControl.

## Horarios configurados

- **Lunes a Viernes**: 9:00 AM (Entrada - Tipo 4)
- **Lunes a Jueves**: 6:30 PM (Salida - Tipo 0)
- **Viernes**: 6:00 PM (Salida - Tipo 0)

## Configuración de Secrets

Para mayor seguridad, configura estas variables en GitHub:

1. Ve a Settings > Secrets and variables > Actions
2. Agrega:
   - `RUT`: Tu RUT (ej: 17.978.432-7)
   - `PASSWORD`: Tu contraseña

## Ejecución

- Automática: Cada 5 minutos (vía GitHub Actions)
- Manual: Desde Actions > "Marcaciones Automáticas" > "Run workflow"
