import os
from gymnasium.wrappers import TimeLimit

from stable_baselines3 import PPO
from gym_lacoro.envs.warehouse_env import WarehouseEnvContinuous

def train():
    # Directorios
    models_dir = "models/PPO"
    os.makedirs(models_dir, exist_ok=True)

    # Nombre del archivo donde guardas tu progreso
    model_path = f"{models_dir}/warehouse_final.zip"
    learning_steps = 100_000

    # 1. Instanciar Entorno
    env = WarehouseEnvContinuous(points_path="/home/kishouandrea/lacoro-reto/ros2_ws/src/warehouse_simulator/resources/points_training.yaml")
    env = TimeLimit(env, 1000)
    
    # 2. LÓGICA DE CARGA (Iteración)
    if os.path.exists(model_path):
        print(f"¡Modelo encontrado en {model_path}!")
        print("Cargando cerebro existente para continuar entrenando...")
        # reset_num_timesteps=False es CLAVE para que sigan sumando las gráficas
        model = PPO.load(model_path, env=env) 
    else:
        print("No existe modelo previo. Creando uno nuevo desde cero...")
        model = PPO(
            'MultiInputPolicy',
            env,
            verbose=1,
            tensorboard_log=models_dir)

    # 3. Entrenar (Iteración)
    # Puedes correr esto muchas veces. Cada vez sumará 10,000 pasos más de experiencia.
    print(f"Iniciando entrenamiento por {learning_steps} pasos más...")
    
    model.learn(total_timesteps=learning_steps,
                log_interval=1,
                progress_bar=True,
                tb_log_name="PPO")

    # 4. Guardar (Sobrescribir para la próxima vez)
    model.save(f"{models_dir}/warehouse_final")
    print("Modelo actualizado y guardado.")

if __name__ == '__main__':
    train()