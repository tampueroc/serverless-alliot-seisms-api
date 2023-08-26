# Serverless Seisms API
## Requirements
- Python 3.10
- Node 18
## Set up
Create virtual environment
```
python -m venv .venv
```
Launch virtual environment
```
source .venv/bin/activate
```
Install python requirements
```
pip install -r requirements.txt
```
## Further information
### Solucion problemas de memoria para las lambdas:
Se utilizo AWS Athena para realizar la query a el bucket de S3 donde se almacena el archivo parquet para almacenar las entradas. El limite de fija en la query SQL para respetar la restriccion de memoria. Con AWS Athena se realiza la query y luego los resultados se guardan en otro bucket de resultados en S3 para ser recuperados posteriormente.

### Solucion descartada (no permitia OFFSET)
Se ocupo la funcionalidad de S3 Select que permite recuperar datos de objetos en un bucket de S3 ocupando queries SQL, se barajo la opcion de ocupar AWS Athena para abordar esta restricción, sin embargo, se opto por ocupar esta funcionalidad igual de efectiva para la tarea bajo el supuesto que se ocupa un unico archivo dentro del bucket para almacenar los datos. AWS Athena es sin lugar a dudas una solucion mas robusta e extensible a diferencia de S3 Select que solo puede resolver queries para un caso particular.


> S3 Select is more appropriate for simple filtering and retrieval of specific subsets of data from S3 objects using basic SQL statements, with reduced data transfer costs and latency. Amazon Athena, on the other hand, is suitable for running complex, ad-hoc queries across multiple paths in Amazon S3, offering more comprehensive SQL capabilities, improved performance, and optimization options. Athena supports more file formats, compression types, and optimizations, while S3 Select is limited to CSV, JSON, and Parquet formats.

Source: [S3 Select vs. AWS Athena – The Quick Comparison](https://ahana.io/learn/comparisons/s3-select-vs-athena-the-quick-comparison/)

References:
- [S3 Select and Glacier Select – Retrieving Subsets of Objects](https://aws.amazon.com/blogs/aws/s3-glacier-select/)
- [Amazon S3 Update: New Storage Class and General Availability of S3 Select](https://aws.amazon.com/blogs/aws/)amazon-s3-update-new-storage-class-general-availability-of-s3-select/

### CI/CD

Se ocupo en conjunto de Github Actions, Github Secrets y Serverless Framework para armar un ciclo de CI/CD seguro protegido por PR a la rama main.

## JSONSchema

Se aplico un JSONSchema a nivel de API Gateaway para añadir otra capa de proteccion al endpoint y validar la estructura y tamaño del payload al momento de crear las entradas (tratando de respetar la restriccion de memorias para Lambda, se asume que al invariante aplica a toda la aplicacion y no solo al metodo GET)

## Layers

Cada Lambda se ejecuta sobre una Layer de la aplicacion, asi se reduce el tamaño de la Lambda y se puede asegurar consistencia y versionamiento sobre las dependencias de la aplicacion.

## Caveats

- Se puede pulir la implementacion añadiendo un manejo de Exceptions mas robusto y revisando los loggings, sin embargo, se manejan los casos borde mas criticos.

- La propiedad timestamp de las entradas esta en formato Unix considera fecha y tiempo (en UTC), sin embargo, los filtros dateLower y dateUpper consideran solo fecha. Esto entrega libertad para definir como abordar la hora, estrictamente se deberia asumir para la cota inferior 00:00 y para la cota superior 23:59.
