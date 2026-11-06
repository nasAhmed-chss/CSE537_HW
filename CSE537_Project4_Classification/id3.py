# id3.py
# -------
# ID3 Decision Tree implementation
import math
import util as util


class ID3Node:
    """
    A single node of the decision tree.

    A leaf node has feature == None and predicts `label`.
    An internal node tests `feature`; `children` maps each feature value seen
    in training to a subtree. `label` holds the majority training label at the
    node, used as the fallback prediction for unseen values and when pruning.
    """

    def __init__(self, label, feature=None, children=None):
        self.label = label
        self.feature = feature
        self.children = children if children is not None else {}

    def isLeaf(self):
        return self.feature is None


class ID3Classifier:
    """
    ID3 Decision Tree classifier.
    """

    def __init__(self, legalLabels):
        self.legalLabels = legalLabels
        self.type = "id3"
        self.tree = None
        self.pruning = False

        # You may initialize additional parameters here.

    def setPruning(self, pruning):
        self.pruning = pruning

    def train(self, trainingData, trainingLabels,
              validationData, validationLabels):
        """
        Train the ID3 decision tree using information gain.
        Apply pruning if enabled.
        """
        "*** YOUR CODE HERE ***"
        features = set()
        for datum in trainingData:
            features.update(datum.keys())

        indices = list(range(len(trainingData)))
        self.tree = self._buildTree(trainingData, trainingLabels, indices, features)
        print("Tree size before pruning: %d nodes" % self._countNodes(self.tree))

        if self.pruning:
            valIndices = list(range(len(validationData)))
            self._prune(self.tree, validationData, validationLabels, valIndices)
            print("Tree size after pruning:  %d nodes" % self._countNodes(self.tree))

    def classify(self, testData):
        """
        Return the predicted labels for the test data.
        """
        "*** YOUR CODE HERE ***"
        return [self._classifyDatum(self.tree, datum) for datum in testData]

    # You may add additional helper methods here.

    def _buildTree(self, data, labels, indices, features):
        """
        Recursively build the ID3 tree for the examples in `indices`,
        choosing splits only from the set `features`.
        """
        majority = self._majorityLabel(labels, indices)

        # base case 1
        if all(labels[i] == labels[indices[0]] for i in indices):
            return ID3Node(labels[indices[0]])

        # base case 2
        if not features:
            return ID3Node(majority)

        # pick feat with highest info gain
        bestFeature, bestGain = None, 0.0
        baseEntropy = self._entropy(labels, indices)
        for f in features:
            gain = baseEntropy - self._splitEntropy(data, labels, indices, f)
            if gain > bestGain:
                bestFeature, bestGain = f, gain

        # base case 3
        if bestFeature is None:
            return ID3Node(majority)

        # parition the data and recurse
        node = ID3Node(majority, feature=bestFeature)
        remaining = features - {bestFeature}
        for value, subset in self._partition(data, indices, bestFeature).items():
            node.children[value] = self._buildTree(data, labels, subset, remaining)
        return node

    def _entropy(self, labels, indices):
        """Entropy of the label distribution over `indices`."""
        counts = util.Counter()
        for i in indices:
            counts[labels[i]] += 1
        total = float(len(indices))
        entropy = 0.0
        for c in counts.values():
            if c > 0:
                p = c / total
                entropy -= p * math.log(p, 2)
        return entropy

    def _splitEntropy(self, data, labels, indices, feature):
        """
        Expected entropy after splitting `indices` on `feature`:
        sum over values v of |S_v|/|S| * Entropy(S_v).
        """
        total = float(len(indices))
        result = 0.0
        for subset in self._partition(data, indices, feature).values():
            result += (len(subset) / total) * self._entropy(labels, subset)
        return result

    def _partition(self, data, indices, feature):
        """Group example indices by their value for `feature`."""
        groups = {}
        for i in indices:
            groups.setdefault(data[i][feature], []).append(i)
        return groups

    def _majorityLabel(self, labels, indices):
        """Most common label among `indices`."""
        counts = util.Counter()
        for i in indices:
            counts[labels[i]] += 1
        return counts.argMax()

    #Classify 

    def _classifyDatum(self, node, datum):
        """Follow the tree from `node` down to a leaf and return its label."""
        while not node.isLeaf():
            child = node.children.get(datum[node.feature])
            if child is None:
                # value never seen 
                return node.label
            node = child
        return node.label

   #Reduce error prunign
    def _prune(self, node, data, labels, indices):
        """
        Bottom-up reduced-error pruning using the validation examples in
        `indices` that reach this node. Returns the number of those examples
        the (possibly pruned) subtree misclassifies.
        """
        leafErrors = sum(1 for i in indices if labels[i] != node.label)
        if node.isLeaf():
            return leafErrors

        # prune children first
        groups = self._partition(data, indices, node.feature)
        subtreeErrors = 0
        for value, child in node.children.items():
            subtreeErrors += self._prune(child, data, labels, groups.get(value, []))
        # example that reach this node
        for value, subset in groups.items():
            if value not in node.children:
                subtreeErrors += sum(1 for i in subset if labels[i] != node.label)

        # repalce subtree with leaf
        if leafErrors <= subtreeErrors:
            node.feature = None
            node.children = {}
            return leafErrors
        return subtreeErrors

    def _countNodes(self, node):
        """Total number of nodes in the subtree rooted at `node`."""
        return 1 + sum(self._countNodes(c) for c in node.children.values()) 