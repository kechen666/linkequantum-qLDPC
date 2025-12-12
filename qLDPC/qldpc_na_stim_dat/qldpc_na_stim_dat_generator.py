import os
import stim

def generate_samples(input_path, output_path, shots):
    with open(input_path, 'r') as f:
        content = f.read()
    circ = stim.Circuit(content)
    circ.compile_detector_sampler().sample_write(shots=shots, filepath=output_path, format="b8", append_observables=True)
    print(f"Generated samples for {input_path}")

def main():
    input_dir = '/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_circuit'
    output_dir = '/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dat'
    shots = 10**4
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.stim') and 'without_measure' not in filename and "Z" in filename:
            print(f"Processing {filename}")
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.stim', '.dat')
            output_path = os.path.join(output_dir, output_filename)
            generate_samples(input_path, output_path, shots)
            print(f"Generated samples for {filename}")

if __name__ == "__main__":
    main()