import os
import stim

def generate_dem(input_path, output_path):
    with open(input_path, 'r') as f:
        content = f.read()
    circ = stim.Circuit(content)
    dem = circ.detector_error_model(flatten_loops=True, decompose_errors=False)
    with open(output_path, 'w') as f:
        dem.to_file(f)

def main():
    input_dir = '/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_circuit'
    output_dir = '/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dem'
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.stim') and 'without_measure' not in filename and "Z" in filename:
            print(f"Processing {filename}")
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.stim', '.dem')
            output_path = os.path.join(output_dir, output_filename)
            generate_dem(input_path, output_path)
            print(f"Generated DEM for {filename}")

if __name__ == "__main__":
    main()