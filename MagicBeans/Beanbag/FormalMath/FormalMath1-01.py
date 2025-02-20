class FormalMathMagicBean:
    def __init__(self, initial_state=0.0, alpha=0.1):
        """
        Initialize the Formal Math Bean with an initial model state.
        :param initial_state: Initial value for M_0
        :param alpha: Sensitivity parameter for confidence tracking
        """
        self.M_n = initial_state  # Initial system state
        self.alpha = alpha  # Sensitivity parameter for confidence tracking

    def update(self, D_n1, L_n1, L_star=0):
        """
        Perform an iterative update using the recurrence relation:
        M_{n+1} = M_n + D_{n+1} - (L_{n+1} + L*)
        :param D_n1: New data (incremental improvement)
        :param L_n1: Known loss or degradation factor
        :param L_star: Emergent loss (optional, if unexpected deviations occur)
        """
        self.M_n = self.M_n + D_n1 - (L_n1 + L_star)
        return self.M_n

    def compute_confidence(self, expected_M_n1):
        """
        Compute confidence based on mismatch between expected and actual values.
        :param expected_M_n1: The expected value for the next iteration
        :return: Confidence score between 0 and 1
        """
        delta = abs(expected_M_n1 - self.M_n)
        confidence = max(0, 1 - self.alpha * delta)
        return confidence

# Example Usage
if __name__ == "__main__":
    bean = FormalMathMagicBean(initial_state=1.0, alpha=0.1)
    print("Initial State:", bean.M_n)
    
    # Example iteration
    updated_state = bean.update(D_n1=0.5, L_n1=0.2)
    print("Updated State:", updated_state)
    
    # Confidence Calculation Example
    confidence_score = bean.compute_confidence(expected_M_n1=1.3)
    print("Confidence Score:", confidence_score)
