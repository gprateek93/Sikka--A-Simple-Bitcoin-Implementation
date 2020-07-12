import matplotlib.pyplot as pyplot

def create_graph(input={}, output={},complexity = None, input_size = 0, output_size = 0):
    plt.style.use("fivethirtyeight")
    fig = plt.figure()
    plts = []
    for i in range(len(input.keys())):
        plts.append(fig.add_subplot(input_size,output_size,i+1))
    for i in range(len(input.keys())):
        key = input.keys()[i]
        plts[i].plot(input[key],output[key])
        plts[i].xlabel = key
        plts[i].ylabel = "Space Complexity" if complexity == "space" else "Time Complexity"
    if complexity == "space":
        plt.title = "Variation in Space Complexity while tuning the hyperparameters of the blockchain"
    else:
        plt.title = "Variation in Time Complexity while tuning the hyperparameters of the blockchain"
    plt.show()