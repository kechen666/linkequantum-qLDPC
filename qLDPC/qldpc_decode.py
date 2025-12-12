import os
import stim

if __name__ == "__main__":
    # Configuration parameters
    stim_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_circuit"
    dem_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dem"
    dat_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_dat"
    result_dir = "/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_result"
    
    tesseract_path = "/home/normaluser/ck/tesseract-decoder/bazel-bin/src/tesseract"
    
    os.makedirs(result_dir, exist_ok=True)
    
    for filename in os.listdir(stim_dir):
        if filename.endswith('.stim') and 'without_measure' not in filename and "Z" in filename:
            # Construct core_name
            print(f"Processing {filename}")
            stim_filename = filename
            dem_filename = filename.replace('.stim', '.dem')
            dat_filename = filename.replace('.stim', '.dat')
            
            # Construct file paths
            circuit_file = os.path.join(stim_dir, stim_filename)
            dem_file = os.path.join(dem_dir, dem_filename)
            dat_file = os.path.join(dat_dir, dat_filename)
            
            # Check if required files exist
            if not os.path.exists(dem_file):
                print(f"Warning: DEM file not found: {dem_file}. Skipping.")
                continue
            if not os.path.exists(dat_file):
                print(f"Warning: DAT file not found: {dat_file}. Skipping.")
                continue
            
            # Check number of observables in the circuit
            try:
                circ = stim.Circuit.from_file(circuit_file)
                num_observables = circ.num_observables
                if num_observables >= 32:
                    print(f"Warning: Circuit has {num_observables} observables, which exceeds tesseract's limit of 32. Skipping.")
                    continue
            except Exception as e:
                print(f"Error loading circuit {circuit_file}: {e}. Skipping.")
                continue
            
            output_file = os.path.join(result_dir, f"decoded_{stim_filename.replace('.stim', '')}.json")
            output_file_pre = os.path.join(result_dir, f"decoded_{stim_filename.replace('.stim', '')}_pre.01")
            
            # Construct the command
            command = (
                f"{tesseract_path} --pqlimit 1000000 --circuit {circuit_file} --dem {dem_file} "
                f"--in {dat_file} --in-format b8 --in-includes-appended-observables --out {output_file_pre} --out-format 01 "
                f"--stats-out {output_file} --threads 128 --beam 23 --num-det-orders 1 "
                f"--no-merge-errors"
            )
            
            # Print or execute the command
            print(f"Running: {command}")
            
            # Uncomment the following line to actually execute the command
            result = os.system(command)
            if result != 0:
                print(f"Error: Command failed for {stim_filename}")
            else:
                print(f"Finished decoding for {stim_filename}")

print("Decoding finished")

# nohup python /home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_decode.py >/home/normaluser/ck/linkequantum-qLDPC/qLDPC/qldpc_na_stim_result/log/qldpc_code.log 2>&1 &
