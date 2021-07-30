from os import path
from sys import argv
import datetime as dt
DATE_FORMAT = "%d.%m.%Y"
DATA = path.join(path.dirname(path.abspath(__file__)), "weight.dat")

def fail(message):
   quit(message + """
Example usage:
weight cat
weight plot
weight add 75.2
""")

def read():
   dates, weights = [], []
   with open(DATA) as f:
      for line in f.readlines():
         date, weight = line.split(" ")
         dates.append(date)
         weights.append(float(weight))
   return dates, weights

def smooth(data, cutoff_freq=0.03):
   import scipy.signal as signal
   N = 3 # filter order
   B, A = signal.butter(N, cutoff_freq, output="ba")
   if len(data) > 12:
      padlen = 3 * max(len(A), len(B))
   else:
      padlen = 0
   return signal.filtfilt(B, A, data, padtype='constant', padlen=padlen)

def plot():
   import numpy as np
   import matplotlib.pyplot as plt

   dates, weights = read()
   data = np.array(weights)
   if len(data) < 2:
      raise ValueError("at least 2 data points required for plotting")

   fig = plt.figure(figsize=(13, 7))
   ax = fig.add_subplot(1, 1, 1)
   
   average = smooth(data)

   idx = np.arange(len(data))
   
   less = smooth(np.where(data < average, data, average))
   more = smooth(np.where(data > average, data, average))

   less_idx, = (data < average).nonzero()
   more_idx, = (data > average).nonzero()
   much_less = smooth(np.interp(idx, less_idx, data[less_idx]))
   much_more = smooth(np.interp(idx, more_idx, data[more_idx]))

   ax.plot(data, "k.", markersize=3)
   ax.plot(average, "r-")
   ax.fill_between(idx, much_less, much_more, color="#aaaaaa")
   ax.fill_between(idx, less, more, color="#884444")

   ax.set_xlabel("Date")
   ax.set_ylabel("Weight [kg]")

   ymin, ymax = np.floor(data.min()), np.ceil(data.max())
   major_ymin = np.floor(data.min()/5)*5
   major_ymax = np.ceil(data.max()/5)*5
   ax.set_yticks(np.arange(major_ymin, major_ymax+1, 5))
   ax.set_yticks(np.arange(ymin, ymax+1), minor=True)

   step = max(1, len(data) // 12)
   ax.set_xticks(np.arange(0, len(data), step))
   ax.set_xticklabels(dates[::step], rotation=40)

   ax.tick_params(axis='y', which='both', left=False)
   ax.grid(axis="y", which="minor", color="k", alpha=0.3)
   ax.grid(axis="y", which="major", color="k")
   ax.set_ylim(ymin, ymax)

   fig.tight_layout()

   plt.show()

def add(weight):
   try:
      float(weight)
   except ValueError:
      fail(f"Cant convert {weight} to float")

   date = dt.date.today().strftime(DATE_FORMAT)
   with open(DATA, "a") as f:
      f.write(f"{date} {weight}\n")
   print(f"Added {weight} to the series succesfully")

if __name__ == "__main__":
   try:
      _, command, *rest = argv
   except ValueError:
      fail("")
   if command == "plot":
      if rest:
         fail("Plot doesn't take arguments.")
      plot()
   elif command == "add":
      try:
         [weight] = rest
      except ValueError:
         fail("Add needs exactly one argument.")
      add(weight)
   elif command == "cat":
      print("...")
      _, weights = read()
      for weight in weights[-30:]:
         print(weight)
   else:
      fail(f"Unknown command: {command}")
