from rtlsdr import RtlSdr
import numpy as np
from scipy.signal import correlate
import time
FS = 1.024e6        # Sampling rate (Hz)
FREQ = 1_575_420_000   # GPS L1 frequency
SAMPLES_PER_MS = int(FS // 1000)  # Number of samples per millisecond
CODE_RATE = 1_023_000
# PRN to G2 tap mappings (from ICD-GPS-200)
PRN_G2_TAPS = {
    1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9), 6: (2, 10),
    7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3), 11: (3, 4), 12: (5, 6),
    13: (6, 7), 14: (7, 8), 15: (8, 9), 16: (9, 10), 17: (1, 4), 18: (2, 5),
    19: (3, 6), 20: (4, 7), 21: (5, 8), 22: (6, 9), 23: (1, 3), 24: (4, 6),
    25: (5, 7), 26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6), 30: (2, 7),
    31: (3, 8), 32: (4, 9)
}

def generate_ca_code(prn):
    g1 = np.ones(10)
    g2 = np.ones(10)
    ca = np.zeros(1023)
    t1, t2 = PRN_G2_TAPS[prn]
    for i in range(1023):
        g1_out = g1[-1]
        g2_out = np.mod(g2[-t1] + g2[-t2], 2)
        ca[i] = np.mod(g1_out + g2_out, 2)
        g1 = np.roll(g1, -1)
        g2 = np.roll(g2, -1)
        g1[-1] = np.mod(g1[2] + g1[9], 2)
        g2[-1] = np.mod(g2[1] + g2[2] + g2[5] + g2[7] + g2[8] + g2[9], 2)
    return 1 - 2 * ca  # Map 0 -> +1, 1 -> -1

def upsample_ca_code(code, target_length):
    upsampled = np.repeat(code, target_length // len(code))
    return upsampled[:target_length]

def acquire_prn(iq_samples, ca_codes):
    detected = []
    for prn, ca_code in ca_codes.items():
        corr = np.abs(correlate(iq_samples, ca_code, mode='valid'))
        peak = np.max(corr)
        if peak > 1000:  # Simple threshold
            print(f"[+] PRN {prn:2d} DETECTED (peak={peak:.1f})")
            detected.append((prn, peak))
    return detected

def main():
    print("Initializing RTL-SDR...")
    sdr = RtlSdr()
    sdr.sample_rate = FS
    sdr.center_freq = FREQ
    sdr.gain = 'auto'

    # Precompute C/A codes upsampled to SDR sample rate
    samples_per_code = int(FS / CODE_RATE * 1023)
    ca_codes = {
        prn: upsample_ca_code(generate_ca_code(prn), samples_per_code)
        for prn in PRN_G2_TAPS
    }

    print("Starting GPS PRN acquisition...")
    try:
        while True:
            _ = sdr.read_samples(SAMPLES_PER_MS * 10)  # Flush buffer
            iq_samples = sdr.read_samples(SAMPLES_PER_MS * 5)
            iq_samples -= np.mean(iq_samples)
            acquire_prn(iq_samples, ca_codes)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping GPS data acquisition...")
    finally:
        sdr.close()
        print("RTL-SDR closed.")

if __name__ == "__main__":
    main()