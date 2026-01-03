import os
import numpy as np
from gymnasium.wrappers import TimeLimit


from stable_baselines3 import TD3
from stable_baselines3.common.noise import NormalActionNoise
from gym_lacoro.envs.warehouse_env import WarehouseEnvContinuous



def train():
    # Directorios
    models_dir = "models/TD3"
    os.makedirs(models_dir, exist_ok=True)

    # Nombre del archivo donde guardas tu progreso
    model_path = f"{models_dir}/warehouse_final.zip"
    memory_steps = 2048
    learning_steps = 250_000
    memory_capacity = 2**16
    exploration_noise = 0.2

    # 1. Instanciar Entorno
    env = WarehouseEnvContinuous(
        points_path="/home/kishouandrea/lacoro-reto/ros2_ws/src/warehouse_simulator/resources/points_training.yaml")
    env = TimeLimit(env, 1000)

    # 2. LÓGICA DE CARGA (Iteración)
    if os.path.exists(model_path):
        print(f"¡Modelo encontrado en {model_path}!")
        print("Cargando cerebro existente para continuar entrenando...")
        # reset_num_timesteps=False es CLAVE para que sigan sumando las gráficas
        model = TD3.load(model_path, env=env) 
    else:
        print("No existe modelo previo. Creando uno nuevo desde cero...")
        # Create action noise because TD3 and DDPG use a deterministic policy
        n_actions = env.action_space.shape[-1]
        action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=exploration_noise * np.ones(n_actions))

        model = TD3(
            'MultiInputPolicy',
            env,
            buffer_size=memory_capacity,  # 1e6
            learning_starts=memory_steps,
            action_noise=action_noise,
            verbose=1,
            tensorboard_log=models_dir)

    # 3. Entrenar (Iteración)
    # Puedes correr esto muchas veces. Cada vez sumará 10,000 pasos más de experiencia.
    print(f"Iniciando entrenamiento por {learning_steps} pasos más...")
    
    model.learn(total_timesteps=(learning_steps + memory_steps),
                log_interval=1,
                progress_bar=True,
                tb_log_name="TD3")

    # 4. Guardar (Sobrescribir para la próxima vez)
    model.save(f"{models_dir}/warehouse_final")
    print("Modelo actualizado y guardado.")

if __name__ == '__main__':
    train()