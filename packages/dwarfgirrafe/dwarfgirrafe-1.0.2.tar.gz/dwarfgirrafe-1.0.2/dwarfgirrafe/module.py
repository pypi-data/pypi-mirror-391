def mlone():
    print(
        """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings 
#We do not want to see warnings
warnings.filterwarnings("ignore") 
#import data
data = pd.read_csv("uber.csv")
#Create a data copy
df = data.copy()
#Print data
df.head()
#Get Info
df.info()
#pickup_datetime is not in required data format
df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
df.info()
#Statistics of data
df.describe()
#Number of missing values
df.isnull().sum()

#Correlation
df.select_dtypes(include=[np.number]).corr()
print(df.columns)
#Drop the rows with missing values
df.dropna(inplace=True)
plt.boxplot(df['fare_amount'])
#Remove Outliers
q_low = df["fare_amount"].quantile(0.01)
q_hi  = df["fare_amount"].quantile(0.99)

df = df[(df["fare_amount"] < q_hi) & (df["fare_amount"] > q_low)]
#Check the missing values now
df.isnull().sum()
#Time to apply learning models
from sklearn.model_selection import train_test_split
#Take x as predictor variable
x = df.drop("fare_amount", axis = 1)
#And y as target variable
y = df['fare_amount']
#Necessary to apply model
x['pickup_datetime'] = pd.to_numeric(pd.to_datetime(x['pickup_datetime']))
x = x.loc[:, x.columns.str.contains('^Unnamed')]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 1)
from sklearn.linear_model import LinearRegression
lrmodel = LinearRegression()
lrmodel.fit(x_train, y_train)

#Prediction
predict = lrmodel.predict(x_test)
# evaluation

from sklearn.metrics import mean_squared_error, r2_score

lr_rmse = np.sqrt(mean_squared_error(y_test, predict))
lr_r2 = r2_score(y_test, predict)

print("Linear Regression → RMSE:", lr_rmse, "R²:", lr_r2)

#Let's Apply Random Forest Regressor
from sklearn.ensemble import RandomForestRegressor
rfrmodel = RandomForestRegressor(n_estimators = 100, random_state = 101)
#Fit the Forest
rfrmodel.fit(x_train, y_train)
rfrmodel_pred = rfrmodel.predict(x_test)
rfr_rmse = np.sqrt(mean_squared_error(y_test, rfrmodel_pred))
rfr_r2 = r2_score(y_test, rfrmodel_pred)

print("Random Forest → RMSE:", rfr_rmse, "R²:", rfr_r2)
        """
    )

def mltwo():
        
        print(
            """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import seaborn as sns
# Load dataset
data = pd.read_csv("diabetes.csv")
print(data.head())
#Check for null or missing values
data.isnull().sum()
# Replace zeros with mean for selected columns
cols_to_replace = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']
for column in cols_to_replace:
    data[column].replace(0, np.nan, inplace=True)
    data[column].fillna(round(data[column].mean(skipna=True)), inplace=True)
    
# Features and target
X = data.iloc[:, :8]   # first 8 columns are features
Y = data['Outcome']    # target column
    
# Split data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
import matplotlib.pyplot as plt

# Visualize outliers using boxplots
plt.figure(figsize=(12, 6))
sns.boxplot(data)
plt.title("Outlier Detection using Boxplots")
plt.show()

# Identify outliers using IQR
Q1 = data.quantile(0.25)
Q3 = data.quantile(0.75)
IQR = Q3 - Q1

# Display count of outliers per column
outliers = ((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).sum()
print("\nNumber of Outliers per Feature:\n", outliers)

# Initialize KNN
knn = KNeighborsClassifier(n_neighbors=5)  # you can change k
knn.fit(X_train, Y_train)

# Predictions
knn_pred = knn.predict(X_test)
# Metrics
cm = confusion_matrix(Y_test, knn_pred)
accuracy = accuracy_score(Y_test, knn_pred)
error_rate = 1 - accuracy
precision = precision_score(Y_test, knn_pred)
recall = recall_score(Y_test, knn_pred)
f1 = f1_score(Y_test, knn_pred)
# Print results
print("Confusion Matrix:\n", cm)
print("Accuracy Score:", accuracy)
print("Error Rate:", error_rate)
print("Precision Score:", precision)
print("Recall Score:", recall)
print("F1 Score:", f1)

accuracy_scores = []

for k in [3, 5, 7]:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, Y_train)
    knn_pred = knn.predict(X_test)
    acc = accuracy_score(Y_test, knn_pred)
    accuracy_scores.append(acc)
    print(f"K = {k} → Accuracy = {acc * 100:.2f}%")

plt.plot([3, 5, 7], accuracy_scores, marker='o')
plt.title("KNN Accuracy vs K Value")
plt.xlabel("K Value")
plt.ylabel("Accuracy")
plt.grid(True)
plt.show()

"""
        )

def mlthree():
    print(
        """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import seaborn as sns
# Load dataset
df = pd.read_csv('sales_data_sample.csv', encoding='unicode_escape')
df.head()

df.info()

# Drop unnecessary columns
to_drop = ['ADDRESSLINE1', 'ADDRESSLINE2', 'STATE', 'POSTALCODE', 'PHONE']
df = df.drop(to_drop, axis=1)
#Check for null values
df.isnull().sum()

df.dtypes

# Select numeric columns only
df_numeric = df.select_dtypes(include=['int64', 'float64'])

# Visualize outliers
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12, 6))
sns.boxplot(data=df_numeric)
plt.title("Outlier Detection using Boxplots (Numeric Columns Only)")
plt.show()

# Identify outliers using IQR
Q1 = df_numeric.quantile(0.25)
Q3 = df_numeric.quantile(0.75)
IQR = Q3 - Q1

# Count outliers per column
outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()
print("\nNumber of Outliers per Numeric Feature:\n", outliers)

#normilization data
scaler = StandardScaler()
#X_scaled = scaler.fit_transform(df_capped)
X_scaled = scaler.fit_transform(df_numeric)
print(" Data normalized using StandardScaler.")

#df_normalized = pd.DataFrame(X_scaled, columns=df_capped.columns)
df_normalized = pd.DataFrame(X_scaled, columns=df_numeric.columns)

print("\nSample of Normalized Data:")
print(df_normalized.head())

print("\nMean of each feature after normalization:\n", df_normalized.mean())
print("\nStandard deviation of each feature after normalization:\n", df_normalized.std())

inertia = []
K = range(1, 11)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)

# Plot the Elbow curve
plt.figure(figsize=(8, 5))
plt.plot(K, inertia, marker='o')
plt.title("Elbow Method to Determine Optimal K")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.grid(True)
plt.show()

from sklearn.metrics import silhouette_score

for k in range (2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    sil_score = silhouette_score(X_scaled, labels)
    print(f"K = {k} → Silhouette Score = {sil_score:.4f}")
    
#Visualize Clusters for K = 3
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_scaled)

plt.figure(figsize=(8,6))
'''sns.scatterplot(
    x=df_capped['SALES'],
    y=df_capped['MSRP'],
    hue=labels,
    palette='Set2'
)'''
sns.scatterplot(
    x=df['SALES'],
    y=df['MSRP'],
    hue=labels,
    palette='Set2'
)

plt.title("K-Means Clustering Visualization (K = 3)")
plt.xlabel("Sales")
plt.ylabel("MSRP")
plt.legend(title='Cluster')
plt.show()
""")
    
def mlfour():
    print(
        """
import matplotlib.pyplot as plt
import numpy as np
# Define the function
def f(x):
    return (x + 3)**2
# Define its derivative (gradient)
def grad_f(x):
    return 2 * (x + 3)
# Gradient Descent Implementation
def gradient_descent(start_x=2, learning_rate=0.1, max_iter=50, tol=1e-6):
    x = start_x
    x_history = [x]
    
    for i in range(max_iter):
        gradient = grad_f(x)
        x_new = x - learning_rate * gradient
        
        x_history.append(x_new)
        
        if abs(x_new - x) < tol:  # convergence check
            break
        
        x = x_new
    
    return x, f(x), x_history
# Run Gradient Descent
min_x, min_y, x_steps = gradient_descent()
print("Local minima at x =", min_x)
print("Minimum value y =", min_y)

# Visualization
x_vals = np.linspace(-6, 2, 100)
y_vals = f(x_vals)
plt.plot(x_vals, y_vals, label='y = (x+3)^2')
plt.scatter(x_steps, [f(x) for x in x_steps], color='red', label='Gradient Descent Steps')
plt.title("Gradient Descent to find Local Minima")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.show()
""")
    

def btone():
    print(
        """
Step 1: Go to Chrome Web Store Extensions Section.
Step 2: Search MetaMask.
Step 3: Check the number of downloads to make sure that the legitimate MetaMask is being installed, as hackers might try to make clones of it.
Step 4: Click the Add to Chrome button.
Step 5: Once installation is complete this page will be displayed. Click on the Get Started button.
Step 6: This is the first time creating a wallet, so click the Create a Wallet button. If there is already a wallet then import the already created using the Import Wallet button.
Step 7: Click I Agree button to allow data to be collected to help improve MetaMask or else click the No Thanks button. The wallet can still be created even if the user will click on the No Thanks button.
Step 8: Create a password for your wallet. This password is to be entered every time the browser is launched and wants to use MetaMask. A new password needs to be created if chrome is uninstalled or if there is a switching of browsers. In that case, go through the Import Wallet button. This is because MetaMask stores the keys in the browser. Agree to Terms of Use
Step 9: Click on the dark area which says Click here to reveal secret words to get your secret phrase.
Step 10: This is the most important step. Back up your secret phrase properly. Do not store your secret phrase on your computer. Please read everything on this screen until you understand it completely before proceeding. The secret phrase is the only way to access your wallet if you forget your password. Once done click the Next button.
Step 11: Click the buttons respective to the order of the words in your seed phrase. In other words, type the seed phrase using the button on the screen. If done correctly the Confirm button should turn blue.
Step 12: Click the Confirm button. Please follow the tips mentioned.
Step 13: One can see the balance and copy the address of the account by clicking on the Account 1 area.
Step 14: One can access MetaMask in the browser by clicking the Foxface icon on the top right. If the Foxface icon is not visible, then click on the puzzle piece icon right next to it.
""")
    
def btthree():
    print(
        """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract StudentManager {
    struct Student {
        uint256 id;
        string name;
        uint8 age;
        string course;
    }

    Student[] private students;
    mapping(uint256 => uint256) private idx;
    uint256 public studentCount;

    uint256 public depositsCount;
    uint256 public lastDepositAmount;
    address public lastSender;

    event StudentAdded(uint256 indexed id, string name);
    event StudentUpdated(uint256 indexed id);
    event StudentRemoved(uint256 indexed id);
    event Received(address indexed from, uint256 amount);
    event FallbackCalled(address indexed from, uint256 amount, bytes data);

    constructor() {
        studentCount = 0;
    }

    function addStudent(string calldata _name, uint8 _age, string calldata _course) external {
        studentCount += 1;
        uint256 newId = studentCount;
        students.push(Student({id: newId, name: _name, age: _age, course: _course}));
        idx[newId] = students.length;
        emit StudentAdded(newId, _name);
    }

    function getStudent(uint256 _id) public view returns (Student memory) {
        uint256 i = idx[_id];
        require(i != 0, "Student not found");
        return students[i - 1];
    }

    function getAllStudents() external view returns (Student[] memory) {
        return students;
    }

    function updateStudent(uint256 _id, string calldata _name, uint8 _age, string calldata _course) external {
        uint256 i = idx[_id];
        require(i != 0, "Student not found");
        Student storage s = students[i - 1];
        s.name = _name;
        s.age = _age;
        s.course = _course;
        emit StudentUpdated(_id);
    }

    function removeStudent(uint256 _id) external {
        uint256 i = idx[_id];
        require(i != 0, "Student not found");
        uint256 arrayIndex = i - 1;
        uint256 lastIndex = students.length - 1;
        if (arrayIndex != lastIndex) {
            Student memory lastStudent = students[lastIndex];
            students[arrayIndex] = lastStudent;
            idx[lastStudent.id] = arrayIndex + 1;
        }
        students.pop();
        idx[_id] = 0;
        emit StudentRemoved(_id);
    }

    function deposit() external payable {
        require(msg.value > 0, "Send ETH");
        depositsCount += 1;
        lastDepositAmount = msg.value;
        lastSender = msg.sender;
        emit Received(msg.sender, msg.value);
    }

    receive() external payable {
        depositsCount += 1;
        lastDepositAmount = msg.value;
        lastSender = msg.sender;
        emit Received(msg.sender, msg.value);
    }

    fallback() external payable {
        depositsCount += 1;
        lastDepositAmount = msg.value;
        lastSender = msg.sender;
        emit FallbackCalled(msg.sender, msg.value, msg.data);
    }

    function getStudentsLength() external view returns (uint256) {
        return students.length;
    }
}
""")
    
def daaone():
    print(
        """
import time

# ---------- Recursive Fibonacci ----------
def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

# ---------- Non-Recursive Fibonacci ----------
def fib_non_recursive(n):
    n1, n2 = 0, 1
    print(n1, n2, end=" ")
    for i in range(2, n):
        n3 = n1 + n2
        print(n3, end=" ")
        n1, n2 = n2, n3
    print()

# ---------- Main Function ----------
def main():
    n = int(input("Enter the number of elements: "))

    print("\nFibonacci Sequence (Recursive): ", end="")
    start1 = time.time()
    for i in range(n):
        print(fib_recursive(i), end=" ")
    end1 = time.time()
    time_recursive = (end1 - start1) * 1_000_000  # microseconds

    print("\n\nFibonacci Sequence (Non-Recursive): ", end="")
    start2 = time.time()
    fib_non_recursive(n)
    end2 = time.time()
    time_nonrecursive = (end2 - start2) * 1_000_000  # microseconds

    # ---------- Time & Space Complexity ----------
    print("\n=== Time and Space Complexity Analysis ===")
    print(f"Recursive Time Taken: {time_recursive:.2f} microseconds")
    print("Recursive Time Complexity: O(2^n)")
    print("Recursive Space Complexity: O(n)\n")

    print(f"Non-Recursive Time Taken: {time_nonrecursive:.2f} microseconds")
    print("Non-Recursive Time Complexity: O(n)")
    print("Non-Recursive Space Complexity: O(1)")

if __name__ == "__main__":
    main()


'''
### **Step 1:** Start the program.

### **Step 2:** Import the `time` module for calculating execution time.

---

### **Step 3:** Define the recursive Fibonacci function `fib_recursive(n)`.

1. If `n <= 1`, return `n`.
2. Otherwise, return `fib_recursive(n - 1) + fib_recursive(n - 2)`.
3. End the function.

---

### **Step 4:** Define the non-recursive Fibonacci function `fib_non_recursive(n)`.

1. Initialize `n1 = 0` and `n2 = 1`.
2. Print `n1` and `n2`.
3. Repeat steps 4–6 for `i` from 2 to `n - 1`:
   4. Calculate `n3 = n1 + n2`.
   5. Print `n3`.
   6. Update `n1 = n2` and `n2 = n3`.
4. Print a newline after the loop ends.
5. End the function.

---

### **Step 5:** Define the main function `main()`.

1. Read input `n` (the number of Fibonacci elements).
2. Print `"Fibonacci Sequence (Recursive):"`.
3. Record `start1 = time.time()`.
4. For each `i` from 0 to `n - 1`:
   Call `fib_recursive(i)` and print the result.
5. Record `end1 = time.time()`.
6. Calculate `time_recursive = (end1 - start1) * 1_000_000` (in microseconds).

---

### **Step 6:** Execute the non-recursive method.

1. Print `"Fibonacci Sequence (Non-Recursive):"`.
2. Record `start2 = time.time()`.
3. Call `fib_non_recursive(n)`.
4. Record `end2 = time.time()`.
5. Calculate `time_nonrecursive = (end2 - start2) * 1_000_000` (in microseconds).

---

### **Step 7:** Display time and complexity analysis.

1. Print `"=== Time and Space Complexity Analysis ==="`.
2. Print:
   • Recursive Time Taken = `time_recursive`
   • Recursive Time Complexity = O(2ⁿ)
   • Recursive Space Complexity = O(n)
3. Print:
   • Non-Recursive Time Taken = `time_nonrecursive`
   • Non-Recursive Time Complexity = O(n)
   • Non-Recursive Space Complexity = O(1)

---

### **Step 8:** Stop the program.
'''

""")
    
def daatwo():
    print(
        """
import heapq

# Creating Huffman tree node
class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq      # Frequency of symbol
        self.symbol = symbol  # Symbol name (character)
        self.left = left      # Node left of current node
        self.right = right    # Node right of current node
        self.huff = ''        # Tree direction (0/1)

    def __lt__(self, nxt):
        return self.freq < nxt.freq


# Function to print Huffman codes
def print_nodes(node, val=''):
    new_val = val + str(node.huff)
    if node.left:
        print_nodes(node.left, new_val)
    if node.right:
        print_nodes(node.right, new_val)
    # If leaf node
    if not node.left and not node.right:
        print(f"{node.symbol} -> {new_val}")


# Main function
if __name__ == "__main__":
    print("----- Huffman Coding -----")

    # Take number of symbols
    n = int(input("Enter the number of characters: "))

    chars = []
    freq = []

    # Taking input from user
    for i in range(n):
        ch = input(f"Enter character {i+1}: ")
        f = int(input(f"Enter frequency of '{ch}': "))
        chars.append(ch)
        freq.append(f)

    # Creating a list of nodes
    nodes = []
    for i in range(len(chars)):
        heapq.heappush(nodes, Node(freq[i], chars[i]))

    # Combine nodes until one remains
    while len(nodes) > 1:
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)

        left.huff = 0
        right.huff = 1

        new_node = Node(left.freq + right.freq, left.symbol + right.symbol, left, right)
        heapq.heappush(nodes, new_node)

    print("\nHuffman Codes for each character:")
    print("--------------------------------")
    print_nodes(nodes[0])

# ouput:
# ----- Huffman Coding -----
# Enter the number of characters: 3
# Enter character 1: A
# Enter frequency of 'A': 5
# Enter character 2: B
# Enter frequency of 'B': 7
# Enter character 3: C
# Enter frequency of 'C': 10

# Huffman Codes for each character:
# --------------------------------
# A -> 00
# B -> 01
# C -> 1


'''


### **Step 1: Input**

Take a set of characters and their corresponding frequencies (or probabilities of occurrence).

---

### **Step 2: Create Leaf Nodes**

For each character, create a **leaf node** containing:

* The character itself
* Its frequency

Put all these nodes into a **priority queue** or **min-heap**, where the node with the smallest frequency has the highest priority.

---

### **Step 3: Build the Huffman Tree**

Repeat the following steps until there is **only one node left** in the heap:

1. **Remove** the two nodes with the **smallest frequencies** from the heap.
2. **Create a new internal node**:

   * Its frequency = sum of the two nodes’ frequencies.
   * Its left child = the first node (assign it a binary digit `0`).
   * Its right child = the second node (assign it a binary digit `1`).
3. **Insert** this new node back into the heap.

When only one node remains, that node becomes the **root of the Huffman Tree**.

---

### **Step 4: Assign Huffman Codes**

* Traverse the tree from the root:

  * Assign `0` for the **left branch**.
  * Assign `1` for the **right branch**.
* The **code for each character** is the sequence of `0`s and `1`s along the path from the root to that character (leaf node).

---

### **Step 5: Encode the Data**

* Replace every character in the input data with its corresponding Huffman code.
* This produces the **compressed bitstream**.

---

### **Step 6: Decode the Data (Optional)**

* To decode, use the Huffman tree.
* Start at the root and follow the bits:

  * `0` → go to left child
  * `1` → go to right child
* When a leaf node is reached, output the character and go back to the root for the next bit sequence.

---

'''


""")

def daathree():
    print(
        """
def fractional_knapsack():
    # Step 1: Take number of items
    n = int(input("Enter number of items: "))

    weights = []
    values = []

    # Step 2: Take weight and value together on same line
    print("\nEnter weight and value for each item (separated by space):")
    for i in range(n):
        w, v = map(float, input(f"Item {i+1}: ").split())
        weights.append(w)
        values.append(v)

    # Step 3: Take knapsack capacity
    capacity = float(input("\nEnter knapsack capacity: "))

    # Step 4: Fractional knapsack logic
    res = 0.0
    items = sorted(zip(weights, values), key=lambda x: x[1] / x[0], reverse=True)

    print("\nItem selection process:")
    for weight, value in items:
        if capacity <= 0:
            break

        if weight <= capacity:
            res += value
            capacity -= weight
            print(f"  Took full item (weight={weight}, value={value})")
        else:
            res += capacity * (value / weight)
            print(f"  Took {capacity} weight fraction of item (weight={weight}, value={value})")
            capacity = 0

    print(f"\n Maximum value in knapsack = {res:.2f}")


if __name__ == "__main__":
    fractional_knapsack()

# Output:
'''Enter number of items: 3

Enter weight and value for each item (separated by space):
Item 1: 10 60
Item 2: 20 100
Item 3: 30 120

Enter knapsack capacity: 50'''

""")
    

def daafour():
    print(
        """
def print_board(board):
    for row in board:
        print(" ".join(str(x) for x in row))
    print()

def is_safe(board, row, col, n):
    for i in range(row):
        if board[i][col] == 1 or \
           (col - row + i >= 0 and board[i][col - row + i] == 1) or \
           (col + row - i < n and board[i][col + row - i] == 1):
            return False
    return True

def solve(board, row, n):
    if row == n:
        print_board(board)
        return
    for col in range(n):
        if is_safe(board, row, col, n):
            board[row][col] = 1
            solve(board, row + 1, n)
            board[row][col] = 0

def n_queens():
    n = int(input("Enter N: "))
    board = [[0]*n for _ in range(n)]
    r, c = map(int, input("Enter first queen position (row col): ").split())
    board[r-1][c-1] = 1
    print("\nInitial board:")
    print_board(board)
    print("Solutions:\n")
    solve(board, 0, n)

if __name__ == "__main__":
    n_queens()

# Output:
# Enter N: 4
# Enter first queen position (row col): 1 2
""")