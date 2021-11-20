import simpy 
import random 
import math
import sys

NUM_TECH = 3 # Numero de tecnicos
NUM_SELL = 2 # Numero de vendedores
NUM_SPEC = 1 # Numero de tecnicos especialistas
TIME_WORK = 480 # Cantidad de minutos de trbajo (Jornada laborar)
CLIENT_POSS = 20 # Valor de Possion para la llegada de los clientes
TECH_POSS = 20 # Valor de Possion para el tiempo de atencion de los tecnicos
SPEC_POSS = 15 # Valor de Possion para el tiempo de atencion de los especialistas
SELL_MIN = 2 # Tiempo minimo de atencion de un vendedor
SELL_MAX = 5 # Tiempo maximo de atencion de un vendedor

PRICE = {1:0, 2:350, 3:500, 4:750}
SEED = 2

collection = 0 # Cantidad de dinero recolectado
count_arravied = 0 # Cantidad de clientes que arrivan al taller
exit_time = [] # Tiempo de partida de cada cliente
sell_served = [] # Tiempo de atencion del vendedor
service_list = [] # Servicio de cada cliente
arrived_time = [] # Tiempo de llegada de cada cliente
workshop_served = [] # Tiempo de atencion en el taller

def HourFormat(minutes, beging=8):
    '''
    Esta funcion convierte los minutos en formato de 24h.

    minutes: Cantidad de minutos transcurridos
    beging: Hora inicial. Por defecto este valor es 8:00

    return: Retorna un string con el formato de 24h de los minutos especificados
    '''
    
    mm = minutes % 60
    mm = f'0{mm}' if mm < 10 else f'{mm}'
   
    hh = int(minutes / 60)
    hh = (hh + beging) % 24
    hh = f'0{hh}' if hh < 10 else f'{hh}'

    return f'{hh}:{mm}' if minutes != -1 else f'--:--'

def GenServer():
    R = random.randint(1, 100)
    if R <= 45: return 1
    elif R <= 70: return 2
    elif R <= 80: return 3
    else: return 4

def SpecialistServed(env, spec, ident, service, prio):
    '''
    Esta funcion describe el comportamiento un de un tecnico especialista
    con respecto al cliente. 

    env: Entorno de simulacion
    spec: Recurso para los tencincos especialistas
    ident: Valor numerico utilizado para identificar al cliente
    service: Valor numerico que especifica el tipo de servicio solicitado
    prio: Valor utilizado para dar prioridad a los clientes
    '''

    global workshop_served
    global collection
    global exit_time

    with spec.request(priority=prio) as request:
        yield request # Esperar a que un especialista este libre

        if workshop_served[ident] != -1: return # Si el cliente ya esta siendo atendido, se pasa al siguiente en cola

        workshop_served[ident] = env.now
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Es atendido por un tecnico especialista')

        R = random.random()
        poss = SPEC_POSS if service == 3 else TECH_POSS
        time = int(-(poss)*math.log(R))
        yield env.timeout(time)
        
        collection += PRICE[service]
        exit_time[ident] = env.now
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Finaliza su servicio y se marcha del taller')
        
def TechnicalServed(env, tech, ident, service, prio):
    '''
    Esta funcion describe el comportamiento un de un tecnico 
    con respecto al cliente. 

    env: Entorno de simulacion
    tech: Recurso para los tencincos
    ident: Valor numerico utilizado para identificar al cliente
    service: Valor numerico que especifica el tipo de servicio solicitado
    prio: Valor utilizado para dar prioridad a los clientes
    '''

    global workshop_served
    global collection
    global exit_time

    with tech.request(priority=prio) as request:
        yield request

        if workshop_served[ident] != -1: return

        workshop_served[ident] = env.now
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Es atendido por un tecnico')

        R = random.random()
        time = int(-(TECH_POSS)*math.log(R))
        yield env.timeout(time)

        collection += PRICE[service]
        exit_time[ident] = env.now
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Finaliza su servicio y se marcha del taller')


def SellingServe(env, tech, spec, ident, service):
    '''
    Esta funcion describe el comportamiento una vez que el cliente
    es atendidio por el vendedor

    env: Entorno de simulacion
    tech: Recurso para los tecnicos
    spec: Recurso para los tencincos especialistas
    ident: Valor numerico utilizado para identificar al cliente
    service: Valor numerico que especifica el tipo de servicio solicitado
    '''

    global sell_served
    global collection
    global exit_time

    sell_served[ident] = env.now # Guardar el tiempo en que el cliente es atendido por el vendedor  

    print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Es atendido por un vendedor')

    if service == 4: # Si el servicio es la compra de un articulo es atendido por el propio vendedor
        R = random.random()
        time = SELL_MAX - SELL_MIN
        service_time = SELL_MIN + int(time*R)
        yield env.timeout(service_time)
        collection += PRICE[service]
        exit_time[ident] = env.now
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Finaliza su servicio y se marcha del taller')
    else:
        yield env.timeout(1) # Esperar 1 min, tiempo utilizado por el vendedor para redirigir a cliente al taller
        print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Esperando por taller')

        if service == 3:
            env.process(SpecialistServed(env, spec, ident, service, 0))
        else:
            env.process(TechnicalServed(env, tech, ident, service, 1))
            env.process(SpecialistServed(env, spec, ident, service, 1))

def ClientArrived(env, sell, tech, spec, ident, service):
    '''
    Esta funcion describe el comportamiento de un cliente una vez que entra al taller

    env: Entorno de simulacion
    sell: Recurso para los vendedores
    tech: Recurso para los tecnicos 
    spec: Recurso para los tencincos especialistas
    ident: Valor numerico utilizado para identificar al cliente
    service: Valor numerico que especifica el tipo de servicio solicitado
    '''
    
    global exit_time
    global sell_served
    global service_list
    global arrived_time 
    global workshop_served
    global count_arravied

    arrived_time.append(env.now) # Guardar tiempo de llegada de cada cliente
    service_list.append(service) # Guardar el servicio requerido por cada cliente

    count_arravied += 1
    
    # Crear instancia del cliente en cada una de las lista
    exit_time.append(0)
    sell_served.append(0)
    workshop_served.append(-1)

    print(f'{HourFormat(env.now)} | Cliente {ident} - Service {service} | Llega al taller')

    with sell.request() as request:
        yield request                                                                               # Esperar a que un vendedor este libre
        yield env.process(SellingServe(env, tech, spec, ident, service))                            # Invocar al proceso del vendedor
        
def Main(env, sell, tech, spec):
    '''
    Funcion principal de la simulacion. Especifica el tiempo de arrivo de cada 
    cliente al taller e inicia el procesos de los clientes dentro del taller

    env: Entorno de simulacion
    sell: Recurso para los vendedores
    tech: Recurso para los tecnicos
    spec: Recurso para los tencincos especialistas
    '''
    print(f'{HourFormat(0)} | Comienza a trabajar el taller')

    count = 0                                                        # Contador para identificar a los clientes
    while True:
        R = random.random()                                          # Generar valor random en intervalo (0,1)
        time = int(-(CLIENT_POSS)*math.log(R))                       # Distribucion exponencial para el tiempo
        if env.now + time > TIME_WORK: break                         # Terminal si se supera el tiempo total de trabajo
        yield env.timeout(time)                                      # Esperar a que transcurra el tiempo
        env.process(ClientArrived(env, sell, tech, spec, count, GenServer()))     # Inicia procesos del cliente dentro del taller
        count += 1

if __name__ == '__main__':
    try:
        random.seed(int(sys.argv[1]))                                                       # Tomar semilla del argumento
    except IndexError:                                                                      # Pero si no existe dicho argumento
        random.seed(SEED)                                                                   # Tomar semilla definada como constante
    
    print('Simulacion del Taller Happy Computing')                                          # Mensaje inicial
    env = simpy.Environment()                                                               # Entorno de simulacion

    sell = simpy.Resource(env, capacity=NUM_SELL)                                           # Recurso para los vendedores
    spec = simpy.PriorityResource(env, capacity=NUM_SPEC)                                   # Recurso para los tecnicos especialistas
    tech = simpy.PriorityResource(env, capacity=NUM_TECH)                                   # Recurso para los tecnicos

    env.process(Main(env, sell, tech, spec))                                                # Invoca al procesos principal
    env.run()                                                                               # Inicial simulacion

    print(f'{HourFormat(env.now)} | Cierra el taller')                                      # Notificar cierre del taller

    #####################################################
    #             Resultados finales                    #
    #####################################################
    all_client = len(service_list)                                                          
    
    time_wait = 0                                                                           
    time_wait_selling = []       
    time_wait_workshop = []
    
    for i in range(all_client):
        time_wait_selling.append(sell_served[i] - arrived_time[i])
        time_wait_workshop.append(workshop_served[i] - sell_served[i] 
            if service_list[i] != 4 else 0)
        time_wait += time_wait_selling[i] + time_wait_workshop[i]

    print('\nResultados\n')

    ##### Exportar todos los datos para un fichero output.txt #####
    file = open('./output.txt', 'w')
    
    print(f'Total de Clientes: {all_client}')
    file.write(f'Total de Clientes: {all_client}\n')

    print(f'Dinero recaudado: ${collection}')
    file.write(f'Dinero recaudado: ${collection}\n')

    print(f'Tiempo total de espera: {time_wait} min')
    file.write(f'Tiempo total de espera: {time_wait} min\n')

    print('|=======================================================================================================================================|')
    print('|       \t|          \t|         \t| Atendidio por \t|        \t| Atendido por \t|        \t|        \t|')
    print('|Cliente\t| Servicio \t| LLegada \t| vendedor      \t| Espera \t| taller       \t| Espera \t| Salida \t|')
    print('|=======================================================================================================================================|')

    file.write('Cliente & Servicio & LLegada & Atendidio por vendedor & Espera & Atendido por taller & Espera & Salida \\\\\n')

    for i in range(all_client):
        print(f'|\t{i}\t|\t{service_list[i]}\t|\t{HourFormat(arrived_time[i])}\t|\t{HourFormat(sell_served[i])}\t\t|\t{time_wait_selling[i]}\t|\t{HourFormat(workshop_served[i])}\t|\t{time_wait_workshop[i]}\t|\t{HourFormat(exit_time[i])}\t|')
        file.write(f'{i}&{service_list[i]} & {HourFormat(arrived_time[i])} & {HourFormat(sell_served[i])} & {time_wait_selling[i]} & {HourFormat(workshop_served[i])} & {time_wait_workshop[i]} & {HourFormat(exit_time[i])}\\\\\n')

    print('|=======================================================================================================================================|')