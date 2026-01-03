from stable_baselines3 import PPO
from warehouse_rl.warehouse_env import WarehouseEnv

def run_evaluation():
    env = WarehouseEnv()
    
    # Cargar modelo (asegurate que la ruta coincida con el train_rl)
    model_path = "models/PPO/warehouse_final.zip"
    
    try:
        model = PPO.load(model_path, env=env)
    except:
        print("No se encontró el modelo. ¡Ejecuta 'entrenar' primero!")
        return

    obs, _ = env.reset()
    print("Evaluando modelo...")
    
    while True:
        # Predecir acción (deterministic=True es obligatorio para evaluación)
        action, _ = model.predict(obs, deterministic=True)
        
        # Ejecutar en simulador
        obs, reward, terminated, truncated, _ = env.step(action)
        
        if terminated:
            obs, _ = env.reset()

if __name__ == '__main__':
    run_evaluation()