"""""
模拟现象级噪声下Majorana Steane code的性能，code在d=20的时候近似达到了d_max=3.
"""""
from multiprocessing import Pool
import numpy as np
from extendedstim import MajoranaCSSCode, Circuit, Code2Circuit


def calculate(circuit,p):
    circuit.noise_amplitude_fix(p, p / 10)
    return circuit.experiment(int(np.floor(100/p)), 'tesseract')


def steane_code(d):
    code=MajoranaCSSCode.SteaneCode()
    circuit:Circuit=Code2Circuit(code,0,0,'phenomenological',d)
    physical_error_rates=np.linspace(1e-3, 1e-2, 20)
    _=circuit.detector_error_model()
    print(_)
    with Pool(processes=len(physical_error_rates)) as pool:
        results=[pool.apply_async(calculate, args=(circuit.copy(),p_temp)) for p_temp in physical_error_rates]
        final_results=[result.get() for result in results]
    logical_failure_rate=np.array(final_results)
    sample_numbers=np.floor(100/physical_error_rates)
    vars=2*3.2905*(logical_failure_rate-logical_failure_rate**2)/np.sqrt(sample_numbers)
    print('vars:', ','.join([str(temp) for temp in vars]))
    print('physical error rate:', ','.join([str(temp) for temp in physical_error_rates]))
    print('logical error rate:', ", ".join([str(temp) for temp in final_results]))
    file=open(f'steane_{d}.txt', 'w')
    file.write('physical error rate:'+','.join([str(temp) for temp in physical_error_rates])+'n')
    file.write('logical error rate:'+', '.join([str(temp) for temp in final_results])+'n')
    file.write('vars:'+','.join([str(temp) for temp in vars])+'n')
    file.close()


if __name__ == '__main__':
    steane_code(20)