import os
from stable_baselines3 import PPO
from warehouse_rl.warehouse_env import WarehouseEnv

def train():
    # Directorios
    models_dir = "models/PPO"
    log_dir = "logs"
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Nombre del archivo donde guardas tu progreso
    model_path = f"{models_dir}/warehouse_final.zip"

    # 1. Instanciar Entorno
    env = WarehouseEnv()

    # 2. LÓGICA DE CARGA (Iteración)
    if os.path.exists(model_path):
        print(f"¡Modelo encontrado en {model_path}!")
        print("Cargando cerebro existente para continuar entrenando...")
        # reset_num_timesteps=False es CLAVE para que sigan sumando las gráficas
        model = PPO.load(model_path, env=env) 
    else:
        print("No existe modelo previo. Creando uno nuevo desde cero...")
        model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

    # 3. Entrenar (Iteración)
    # Puedes correr esto muchas veces. Cada vez sumará 10,000 pasos más de experiencia.
    TIMESTEPS = 10000 
    print(f"Iniciando entrenamiento por {TIMESTEPS} pasos más...")
    
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)

    # 4. Guardar (Sobrescribir para la próxima vez)
    model.save(f"{models_dir}/warehouse_final")
    print("Modelo actualizado y guardado.")

if __name__ == '__main__':
    train()