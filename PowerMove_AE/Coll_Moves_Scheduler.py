Fidelity_Atom_Transfer = 0.999
MUS_PER_FRM = 8

def check_conflict(pos, pre_move, move, dim):
    q0 = move[0]
    q1 = move[1]
    pq0 = pre_move[0]
    pq1 = pre_move[1]
    src0 = pos[pq0][dim]
    src1 = pos[q0][dim]
    dst0 = pq1[dim]
    dst1 = q1[dim]    

    if src1 - src0 == 0:
        dir_src = 0
    else:
        dir_src = (src1 - src0) // abs(src1 - src0)
    
    if dst1 - dst0 == 0:
        dir_dst = 0
    else:
        dir_dst = (dst1 - dst0) // abs(dst1 - dst0)
    
    if dir_dst != dir_src:    
        return True
    else:
        return False
    
def coll_moves_scheduler(n, move_distance, move_group, pos, num_aod, move_in_qubits, move_out_qubits, qubits_not_in_storage, cir_qubit_idle_time, cir_fidelity_atom_transfer, list_transfer_duration, list_movement_duration, num_movement_stage):
    def get_distance(move):
        # return conflict_graph.nodes[move]['move_distance']
        return move_distance[move]

    moves = move_group
    moves.sort(key = get_distance)
    print(moves)

    parallel_move_groups = []
    for move in moves:
        flag = False
        for i in range(len(parallel_move_groups)):
            pg = parallel_move_groups[i]
            in_group_flag = True
            for pre_move in pg:
                if check_conflict(pos, pre_move, move, 0) or check_conflict(pos, pre_move, move, 1):
                    in_group_flag = False
                    break
            if in_group_flag:
                parallel_move_groups[i].append(move)
                flag = True
                break
        
        if not flag:
            parallel_move_groups.append([move])
    ms_index = 0
    while ms_index < len(parallel_move_groups):
        max_distance = 0
        for i in range(num_aod):
            if ms_index == len(parallel_move_groups):
                break
            ms = parallel_move_groups[ms_index]
            
            list_active_qubits = []
            for m in ms:
                list_active_qubits.append(m[0])
                if m[0] in move_in_qubits:
                    move_in_qubits.remove(m[0])
                if m[0] in move_out_qubits:
                    move_out_qubits.remove(m[0])
            cir_fidelity_atom_transfer *= pow(Fidelity_Atom_Transfer, len(list_active_qubits))
            for i in range(n):
                if i not in list_active_qubits and ((i in qubits_not_in_storage and i not in move_out_qubits) or i in move_in_qubits):
                    cir_qubit_idle_time[i] = cir_qubit_idle_time[i] + MUS_PER_FRM * 2

            ms.sort(reverse = True, key = get_distance)
            max_distance = max(max_distance, get_distance(ms[0]))
            ms_index += 1
        num_movement_stage += 1
        move_duration = 200*(max_distance /110)**(1/2)
        for i in range(n):
            if (i in qubits_not_in_storage and i not in move_out_qubits) or i in move_in_qubits:
                cir_qubit_idle_time[i] += move_duration
        list_transfer_duration.append(2 * MUS_PER_FRM)
        list_movement_duration.append(move_duration)
    return parallel_move_groups, num_movement_stage, cir_qubit_idle_time, cir_fidelity_atom_transfer, list_transfer_duration, list_movement_duration