## Requerimientos

* `pythin3-simpy`

## Con respecto al programa

Al inicio del código se encuentran una serie de constantes que indican todos los valores requeridos durante la simulación.
Para el caso de que se quiera probar la simulación con otros parámetros basta con cambiar los valores de estas constantes.
Después de las constantes existen una serie de variables globales, donde se van a almacenar todos los valores que serán 
empleados después en el análisis de los resultados.

Una vez que se inicie la simulación el programa ira mostrando mensajes en consola donde se describen todos los eventos que esta 
ocurriendo en la simulación.
Una vez concluida la simulación se muestra en consola un tipo de tabla que contiene la información recopilada durante la simulación.
Eta información también es exportada a un fichero externo llamada `output.txt` pero esta vez con un formato que permite
copiarlo directo sobre un documento latex.

Al inicio de la simulación se especifica un semilla de la biblioteca random, esta esta definida como una de las constantes del programa, 
pero para mayor comodidad, esta puede ser pasada como argumento una vez que se ejecuta el programa.

## Ejecución del programa

```bash
python3 main.py [num]

#num: Valor de la semilla que quieres ejecutar
```

github link: https://github.com/Reinaldo14/Happy-Computing.git
