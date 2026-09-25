# Mensajes enviados

Dashboard de Streamlit para analizar los CSV de mensajes ubicados en la raíz del proyecto.

## Ejecución

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación descubre todos los archivos `*.csv` al iniciar. Para incorporar otro corte, colócalo en esta carpeta y recarga la página. Cada fila representa un agregado de mensajes: se conservan las filas de todos los archivos, incluso si comparten valores, porque pueden representar envíos distintos. Evita cargar dos copias del mismo corte.

## Datos esperados

Los CSV deben incluir `fecha`, `hora`, `cuenta`, `billed`, `failed`, `excluded`, `provider`, `message_type`, `alias_provider`, `network_id` y `reason`. Pueden contener columnas adicionales, como `segments` o `total_characters`.

`cuenta` indica el número de mensajes de la fila. Los estados `billed`, `failed` y `excluded` se interpretan como booleanos; el conteo de cada estado es la suma de `cuenta` de las filas marcadas. Estos estados no se consideran mutuamente excluyentes. Los conteos vacíos se tratan como cero, los negativos como cero y los registros sin fecha válida o con hora fuera de 0 a 23 se descartan.

## Métricas

- Volumen total y conteos de mensajes facturados, fallidos y excluidos.
- Tasas de cada estado sobre el total de mensajes seleccionado.
- Comparación mensual acumulada hasta el último día del periodo filtrado frente al mismo corte del mes anterior; sin base previa se muestra "Sin base".
- Evolución y variación por mes, fecha y hora, con matriz de indicadores.
- Participación y filtros por proveedor, tipo de mensaje, alias, red y motivo.
- Mapas de calor de volumen y tasas por día de la semana y hora; los porcentajes se calculan dividiendo los conteos por el volumen de cada celda.
- Señales operativas de concentración, picos y fallos.