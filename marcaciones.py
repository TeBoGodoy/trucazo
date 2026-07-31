# .github/workflows/marcaciones.yml
name: Marcaciones Automáticas

on:
  schedule:
    # ⬇️ HORARIOS EN UTC (AJUSTADOS PARA CHILE)
    # Invierno (UTC-4): 9:00=13:00, 18:30=22:30, 18:00=22:00
    - cron: '0 13 * * 1-5'     # 9:00 Chile invierno
    - cron: '30 22 * * 1-4'    # 18:30 Chile invierno
    - cron: '0 22 * * 5'       # 18:00 Chile invierno
    
    # Verano (UTC-3): 9:00=12:00, 18:30=21:30, 18:00=21:00
    - cron: '0 12 * * 1-5'     # 9:00 Chile verano
    - cron: '30 21 * * 1-4'    # 18:30 Chile verano
    - cron: '0 21 * * 5'       # 18:00 Chile verano
    
    # Respaldo cada 5 min
    - cron: '*/5 * * * *'
  
  workflow_dispatch:

jobs:
  enviar-marcaciones:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install requests pytz
      - run: python marcaciones.py
        env:
          URL_API: ${{ secrets.URL_API }}
          RUT: ${{ secrets.RUT }}
          PASSWORD: ${{ secrets.PASSWORD }}
