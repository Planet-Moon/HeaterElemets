import matplotlib.pyplot as plt
import numpy as np

def sinGen(steps, amp):
    hour_vector = np.linspace(0,24,steps)
    power_vector = np.cos(hour_vector*0.26) * -amp/2 + amp/2
    return power_vector, hour_vector

def main():
    power_vector, hour_vector  = sinGen(24*60,5000)
    fig,ax = plt.subplots(1,1)
    ax.plot(hour_vector,power_vector)
    plt.show()

if __name__ == '__main__':
    main()
