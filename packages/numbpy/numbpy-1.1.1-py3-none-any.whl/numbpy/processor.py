"""
Hyperspectral Cube Processing Library (v2.2.0 - Simplified API + ML Demonstrations)

Provides a CubeProcessor for hyperspectral cube processing, along with MLExamples
for educational machine learning code snippets (PCA, KMeans, KNN, Linear Regression).
"""

import numpy as np
import pandas as pd
import spectral as spy
import os
import gc
from typing import Tuple, Optional
import random
_version_ = "2.2.0"
_author_ = "Prasad, Aryan, Tanishka"


class CubeProcessor:
    """
    Main class for processing hyperspectral data cubes via a memory-efficient pipeline.
    """

    def _init_(self, verbose: bool = True):
        self.verbose = verbose
        self.source_metadata = {}

    def _print(self, message: str):
        if self.verbose:
            print(message)

    def open_cube(self, hdr_path: str, data_path: str) -> spy.io.spyfile.SpyFile:
        if not os.path.exists(hdr_path) or not os.path.exists(data_path):
            raise FileNotFoundError("Header or data file not found")

        img = spy.envi.open(hdr_path, data_path)
        self.source_metadata = {
            'samples': img.shape[1],
            'lines': img.shape[0],
            'bands': img.shape[2],
            'byte order': img.byte_order,
            'interleave': img.interleave
        }

        self._print(f"Cube opened (not loaded). Shape: {img.shape}")
        return img

    def parse_geometric_param(self, file_path: str, fallback_value: float = 0.0) -> float:
        if not os.path.exists(file_path):
            self._print(f"Geometric param file not found. Using fallback: {fallback_value}")
            return fallback_value

        values = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) > 0:
                        try:
                            values.append(float(parts[-1]))
                        except ValueError:
                            continue

            if values:
                mean_val = np.mean(values)
                self._print(f"Parsed geometric parameter: {mean_val:.2f}")
                return mean_val
            else:
                self._print(f"No valid values found. Using fallback: {fallback_value}")
                return fallback_value

        except Exception as e:
            self._print(f"Error parsing file: {e}. Using fallback: {fallback_value}")
            return fallback_value

    def load_flux_data(self, file_path: str) -> np.ndarray:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Flux data file not found: {file_path}")

        flux_data = np.loadtxt(file_path)
        flux_vector = flux_data[:, 1]
        self._print(f"Flux data loaded. Shape: {flux_vector.shape}")
        return flux_vector

    def radiance_to_reflectance(
        self,
        radiance_img: spy.io.spyfile.SpyFile,
        output_path_base: str,
        flux_data: np.ndarray,
        incidence_angle_deg: float,
        distance_au: float = 1.0,
        band_range: Tuple[int, int] = (5, 255),
        chunk_size: int = 256,
        interleave_format: str = 'bsq'
    ):
        self._print("Streaming radiance-to-reflectance conversion...")

        valid_formats = ['bsq', 'bil', 'bip']
        if interleave_format.lower() not in valid_formats:
            raise ValueError(f"Invalid interleave_format. Choose from {valid_formats}")

        cos_i = np.cos(np.deg2rad(incidence_angle_deg))
        eps = 1e-12

        start_band, end_band = band_range
        flux_data_cleaned = flux_data[start_band:end_band]

        lines, samples, _ = radiance_img.shape
        num_output_bands = end_band - start_band

        output_metadata = {
            'description': 'Reflectance Cube',
            'samples': str(samples),
            'lines': str(lines),
            'bands': str(num_output_bands),
            'data type': '4',
            'interleave': interleave_format,
            'file type': 'ENVI Standard',
            'byte order': self.source_metadata.get('byte order', 0)
        }

        output_hdr_path = output_path_base + '.hdr'
        os.makedirs(os.path.dirname(output_hdr_path), exist_ok=True)
        refl_file = spy.envi.create_image(
            output_hdr_path, output_metadata, ext='.qub', force=True
        )
        refl_mm = refl_file.open_memmap(writable=True)

        denominator = flux_data_cleaned[None, None, :] * cos_i * (distance_au**2) + eps

        for i in range(0, lines, chunk_size):
            chunk_end = min(i + chunk_size, lines)
            radiance_chunk = radiance_img[i:chunk_end, :, start_band:end_band]
            reflectance_chunk = (np.pi * radiance_chunk) / denominator
            refl_mm[i:chunk_end, :, :] = reflectance_chunk

        del refl_mm, refl_file
        gc.collect()
        self._print(f"Reflectance conversion complete. Saved to: {output_hdr_path}")

    def destripe_cube(
        self,
        input_img: spy.io.spyfile.SpyFile,
        output_path_base: str,
        method: str = 'median',
        chunk_size: int = 256,
        interleave_format: str = 'bsq'
    ):
        self._print(f"Destriping cube using two-pass '{method}' method...")

        valid_formats = ['bsq', 'bil', 'bip']
        if interleave_format.lower() not in valid_formats:
            raise ValueError(f"Invalid interleave_format. Choose from {valid_formats}")

        lines, samples, bands = input_img.shape
        col_stats = np.zeros((bands, samples))

        for i in range(bands):
            band_view = input_img.read_band(i)
            if method == 'median':
                col_stats[i, :] = np.median(band_view, axis=0)
            elif method == 'mean':
                col_stats[i, :] = np.mean(band_view, axis=0)
            else:
                raise ValueError("Method must be 'median' or 'mean'")

        output_metadata = {
            'description': 'Destriped Cube',
            'samples': str(samples),
            'lines': str(lines),
            'bands': str(bands),
            'data type': '4',
            'interleave': interleave_format,
            'file type': 'ENVI Standard',
            'byte order': input_img.byte_order
        }

        output_hdr_path = output_path_base + '.hdr'
        os.makedirs(os.path.dirname(output_hdr_path), exist_ok=True)
        destriped_file = spy.envi.create_image(
            output_hdr_path, output_metadata, ext='.qub', force=True
        )
        destriped_mm = destriped_file.open_memmap(writable=True)

        for i in range(0, lines, chunk_size):
            chunk_end = min(i + chunk_size, lines)
            chunk = input_img[i:chunk_end, :, :]
            corrected_chunk = chunk - col_stats[None, :, :]
            destriped_mm[i:chunk_end, :, :] = corrected_chunk

        del destriped_mm, destriped_file
        gc.collect()
        self._print(f"Destriping complete. Saved to: {output_hdr_path}")


# ==============================================================
# Machine Learning Demonstration Utilities
# ==============================================================
class MLExamples:
    """Educational ML & algorithm examples (prints code as plaintext)."""
    
    def bst_patient(self):
        print('''\
#include <iostream>
using namespace std;

class PatientNode {
public:
    int patientId;
    string patientName;
    PatientNode *left, *right;

    PatientNode(int id, string name) {
        patientId = id;
        patientName = name;
        left = right = NULL;
    }
};

PatientNode* insertPatient(PatientNode* root, int id, string name) {
    if (root == NULL) return new PatientNode(id, name);
    if (id < root->patientId) root->left = insertPatient(root->left, id, name);
    else if (id > root->patientId) root->right = insertPatient(root->right, id, name);
    return root;
}

void displayInorder(PatientNode* root) {
    if (root == NULL) return;
    displayInorder(root->left);
    cout << root->patientId << " " << root->patientName << endl;
    displayInorder(root->right);
}

void searchPatient(PatientNode* root, int id) {
    if (root == NULL) {
        cout << "Patient not found.\\n";
        return;
    }
    if (id == root->patientId)
        cout << "Patient Found: " << root->patientName << endl;
    else if (id < root->patientId)
        searchPatient(root->left, id);
    else
        searchPatient(root->right, id);
}

PatientNode* findMinPatient(PatientNode* root) {
    if (root == NULL || root->left == NULL) return root;
    return findMinPatient(root->left);
}

PatientNode* findMaxPatient(PatientNode* root) {
    if (root == NULL || root->right == NULL) return root;
    return findMaxPatient(root->right);
}

int countTotalPatients(PatientNode* root) {
    if (root == NULL) return 0;
    return 1 + countTotalPatients(root->left) + countTotalPatients(root->right);
}

int countLeafPatients(PatientNode* root) {
    if (root == NULL) return 0;
    if (root->left == NULL && root->right == NULL) return 1;
    return countLeafPatients(root->left) + countLeafPatients(root->right);
}

int calculateTreeHeight(PatientNode* root) {
    if (root == NULL) return 0;
    int leftHeight = calculateTreeHeight(root->left);
    int rightHeight = calculateTreeHeight(root->right);
    return (leftHeight > rightHeight ? leftHeight : rightHeight) + 1;
}

int main() {
    PatientNode* root = NULL;
    int choice;

    do {
        cout << "\\n1. Insert Patient Record\\n2. Search Patient by ID\\n3. Display All Records (Inorder)\\n";
        cout << "4. Find Min & Max Patient ID\\n5. Display Counts & Height\\n6. Exit\\nEnter your choice: ";
        cin >> choice;

        if (choice == 1) {
            int id; string name;
            cout << "Enter Patient ID and Name: ";
            cin >> id >> name;
            root = insertPatient(root, id, name);
        } 
        else if (choice == 2) {
            int id;
            cout << "Enter Patient ID to search: ";
            cin >> id;
            searchPatient(root, id);
        } 
        else if (choice == 3) {
            cout << "\\nPatient Records (Inorder):\\n";
            displayInorder(root);
        } 
        else if (choice == 4) {
            PatientNode* minNode = findMinPatient(root);
            PatientNode* maxNode = findMaxPatient(root);
            if (minNode && maxNode) {
                cout << "Minimum Patient ID: " << minNode->patientId << " (" << minNode->patientName << ")\\n";
                cout << "Maximum Patient ID: " << maxNode->patientId << " (" << maxNode->patientName << ")\\n";
            } else {
                cout << "No records found.\\n";
            }
        } 
        else if (choice == 5) {
            cout << "Total Patients: " << countTotalPatients(root) << endl;
            cout << "Leaf Patients: " << countLeafPatients(root) << endl;
            cout << "Tree Height: " << calculateTreeHeight(root) << endl;
        }
    } while (choice != 6);

    return 0;
}
''')

    def expression_tree(self):
        print('''\
#include <iostream>
#include <stack>
#include <string>
#include <algorithm>
#include <vector>
using namespace std;

// Node structure for Expression Tree
struct Node {
    char data;
    Node *left, *right;
    Node(char val) {
        data = val;
        left = right = NULL;
    }
};

// Function to build Expression Tree from Prefix Expression
Node* buildExpressionTree(string prefix) {
    stack<Node*> st;

    // Traverse from right to left
    for (int i = prefix.length() - 1; i >= 0; i--) {
        char ch = prefix[i];
        Node* node = new Node(ch);

        // If it's operator, pop two operands and make them children
        if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '^') {
            node->left = st.top(); st.pop();
            node->right = st.top(); st.pop();
        }

        // Push current node to stack
        st.push(node);
    }
    return st.top();
}

// Traversals
void inorder(Node* root) {
    if (root == NULL) return;
    inorder(root->left);
    cout << root->data << " ";
    inorder(root->right);
}

void preorder(Node* root) {
    if (root == NULL) return;
    cout << root->data << " ";
    preorder(root->left);
    preorder(root->right);
}

void postorder(Node* root) {
    if (root == NULL) return;
    postorder(root->left);
    postorder(root->right);
    cout << root->data << " ";
}

// Height of tree
int height(Node* root) {
    if (root == NULL) return 0;
    return 1 + max(height(root->left), height(root->right));
}

// Count operators
int countOperators(Node* root) {
    if (root == NULL) return 0;
    if (root->data == '+' || root->data == '-' || root->data == '*' || root->data == '/' || root->data == '^')
        return 1 + countOperators(root->left) + countOperators(root->right);
    else
        return countOperators(root->left) + countOperators(root->right);
}

// Mirror tree
void mirror(Node* root) {
    if (root == NULL) return;
    mirror(root->left);
    mirror(root->right);
    swap(root->left, root->right);
}

// Display all traversals of a tree
void displayTraversals(Node* root) {
    cout << "\\nInorder: "; inorder(root);
    cout << "\\nPreorder: "; preorder(root);
    cout << "\\nPostorder: "; postorder(root);
    cout << endl;
}

int main() {
    vector<Node*> trees;
    int choice;

    do {
        cout << "\\n===== Expression Tree Menu =====";
        cout << "\\n1. Construct Expression Tree";
        cout << "\\n2. Display Traversals (Inorder, Preorder, Postorder)";
        cout << "\\n3. Compare Height of Trees";
        cout << "\\n4. Find Tree with Maximum Operators";
        cout << "\\n5. Display Mirrored Version of All Trees";
        cout << "\\n6. Exit";
        cout << "\\nEnter choice: ";
        cin >> choice;

        switch (choice) {
        case 1: {
            string prefix;
            cout << "Enter prefix expression: ";
            cin >> prefix;
            Node* root = buildExpressionTree(prefix);
            trees.push_back(root);
            cout << "Expression Tree created successfully!\\n";
            break;
        }
        case 2: {
            for (int i = 0; i < trees.size(); i++) {
                cout << "\\nTree " << i + 1 << " Traversals:";
                displayTraversals(trees[i]);
            }
            break;
        }
        case 3: {
            cout << "\\nHeights of Expression Trees:\\n";
            for (int i = 0; i < trees.size(); i++) {
                cout << "Tree " << i + 1 << ": " << height(trees[i]) << endl;
            }
            break;
        }
        case 4: {
            int maxOps = -1, index = -1;
            for (int i = 0; i < trees.size(); i++) {
                int ops = countOperators(trees[i]);
                if (ops > maxOps) {
                    maxOps = ops;
                    index = i;
                }
            }
            cout << "\\nTree with maximum operators is Tree " << index + 1 
                 << " with " << maxOps << " operators.\\n";
            break;
        }
        case 5: {
            for (int i = 0; i < trees.size(); i++) {
                mirror(trees[i]);
                cout << "\\nMirrored Tree " << i + 1 << ":";
                displayTraversals(trees[i]);
            }
            break;
        }
        case 6:
            cout << "\\nExiting program...\\n";
            break;
        default:
            cout << "\\nInvalid choice! Try again.\\n";
        }

    } while (choice != 6);

    return 0;
}
''')

    def heap_stock(self):
        print('''\
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    priority_queue<int> maxHeap; // for maximum price
    priority_queue<int, vector<int>, greater<int>> minHeap; // for minimum price

    int n, price;
    cout << "Enter number of days: ";
    cin >> n;

    cout << "Enter daily stock prices:\\n";
    for (int i = 0; i < n; i++) {
        cin >> price;
        maxHeap.push(price);
        minHeap.push(price);
    }

    cout << "\\nMaximum Price: " << maxHeap.top();
    cout << "\\nMinimum Price: " << minHeap.top();

    // Delete topmost (maximum) price
    cout << "\\n\\nDeleting topmost (maximum) price...\\n";
    maxHeap.pop();

    // Display all prices in descending order (using max heap)
    cout << "\\nPrices in Descending Order: ";
    priority_queue<int> tempMax = maxHeap;
    while (!tempMax.empty()) {
        cout << tempMax.top() << " ";
        tempMax.pop();
    }

    // Display all prices in Ascending Order (using min heap)
    cout << "\\nPrices in Ascending Order: ";
    priority_queue<int, vector<int>, greater<int>> tempMin = minHeap;
    while (!tempMin.empty()) {
        cout << tempMin.top() << " ";
        tempMin.pop();
    }

    cout << endl;
    return 0;
}
''')

    def astar(self):
        print('''\
def astar(start, stop):
    open_set = {start}
    closed_set = set()
    g, parents = {start: 0}, {start: start}

    while open_set:
        n = None
        for v in open_set:
            if n is None or g[v] + heuristic(v) < g[n] + heuristic(n):
                n = v

        if n == stop:
            path = []
            while parents[n] != n:
                path.append(n)
                n = parents[n]
            path.append(start)
            path.reverse()
            print("Path found:", path)
            return path

        for (m, w) in get_neighbours(n):
            if m not in open_set and m not in closed_set:
                open_set.add(m)
                parents[m] = n
                g[m] = g[n] + w
            elif g[m] > g[n] + w:
                g[m] = g[n] + w
                parents[m] = n
                if m in closed_set:
                    closed_set.remove(m)
                    open_set.add(m)

        open_set.remove(n)
        closed_set.add(n)

    print("Path not found")
    return None


def get_neighbours(n):
    return Graph.get(n, [])


def heuristic(n):
    h = {'A': 11, 'B': 6, 'C': 99, 'D': 1, 'E': 7, 'G': 0}
    return h.get(n, float('inf'))


Graph = {
    'A': [('B', 2), ('E', 3)],
    'B': [('C', 1), ('G', 9)],
    'C': [],
    'D': [('G', 1)],
    'E': [('D', 6)],
}

astar('A', 'G')
''')

    def server_network(self):
        print('''\
#include <iostream>
using namespace std;
#define MAX 5   // number of servers

// Structure for adjacency list node
struct Node {
    int vertex;
    Node* next;
};

// Adjacency matrix (0 = no connection, 1 = connected)
int adjMatrix[MAX][MAX] = {
    {0, 1, 1, 0, 0},
    {1, 0, 1, 1, 0},
    {1, 1, 0, 0, 1},
    {0, 1, 0, 0, 1},
    {0, 0, 1, 1, 0}
};

// Array of linked lists (Adjacency List)
Node* adjList[MAX] = {NULL};

// Function to create a new node
Node* createNode(int v) {
    Node* newNode = new Node;
    newNode->vertex = v;
    newNode->next = NULL;
    return newNode;
}

// Build adjacency list from matrix
void buildAdjList() {
    for (int i = 0; i < MAX; i++) {
        for (int j = 0; j < MAX; j++) {
            if (adjMatrix[i][j] == 1) {
                Node* newNode = createNode(j);
                newNode->next = adjList[i];
                adjList[i] = newNode; // insert at head (simple way)
            }
        }
    }
}

// Display adjacency matrix
void displayMatrix() {
    cout << "Adjacency Matrix:\\n";
    for (int i = 0; i < MAX; i++) {
        for (int j = 0; j < MAX; j++)
            cout << adjMatrix[i][j] << " ";
        cout << endl;
    }
}

// Display adjacency list
void displayList() {
    cout << "\\nAdjacency List:\\n";
    for (int i = 0; i < MAX; i++) {
        cout << "Server " << i << " -> ";
        Node* temp = adjList[i];
        while (temp != NULL) {
            cout << temp->vertex << " ";
            temp = temp->next;
        }
        cout << endl;
    }
}

// DFS traversal for connectivity
void dfs(int node, bool visited[]) {
    visited[node] = true;
    Node* temp = adjList[node];
    while (temp != NULL) {
        if (!visited[temp->vertex])
            dfs(temp->vertex, visited);
        temp = temp->next;
    }
}

// Check if all servers are reachable
void checkConnectivity(int start) {
    bool visited[MAX] = {false};
    dfs(start, visited);
    bool allReachable = true;
    for (int i = 0; i < MAX; i++) {
        if (!visited[i]) {
            allReachable = false;
            break;
        }
    }
    if (allReachable)
        cout << "\\nAll servers are reachable from Server " << start << ".\\n";
    else
        cout << "\\nNot all servers are reachable from Server " << start << ".\\n";
}

int main() {
    buildAdjList();
    displayMatrix();
    displayList();
    int start = 0;
    checkConnectivity(start);
    return 0;
}
''')

    def n_queens(self):
        print('''\
N = 4
def print_solution(board):
    for row in board:
        print(" ".join("Q" if col else "." for col in row))
    print()

def is_safe(board, row, col):
    for i in range(row):
        if board[i][col]:
            return False

    i, j = row, col
    while i >= 0 and j >= 0:
        if board[i][j]:
            return False
        i -= 1
        j -= 1

    i, j = row, col
    while i >= 0 and j < N:
        if board[i][j]:
            return False
        i -= 1
        j += 1

    return True

def solve_n_queens(board, row=0):
    if row == N:
        print_solution(board)
        return True
    for col in range(N):
        if is_safe(board, row, col):
            board[row][col] = 1
            solve_n_queens(board, row + 1)
            board[row][col] = 0
    return False

board = [[0]*N for _ in range(N)]
solve_n_queens(board)


# N-Queens using Branch and Bound
N = 4
cols = [False]*N
diag1 = [False]*(2*N)
diag2 = [False]*(2*N)
board = [-1]*N

def solve(row):
    if row == N:
        print(board)
        return
    for col in range(N):
        if not cols[col] and not diag1[row+col] and not diag2[row-col+N]:
            board[row] = col
            cols[col] = diag1[row+col] = diag2[row-col+N] = True
            solve(row+1)
            cols[col] = diag1[row+col] = diag2[row-col+N] = False

solve(0)
''')
    
    def list_programs(self):
        print('''\
Available Programs:
 1. BST Patient Management
 2. AVL Employee Management
 3. Fractional Knapsack (Food)
 4. Fractional Knapsack (Truck)
 5. Knapsack File Management
 6. Max-Min Heap Job Priority
 7. Flight Graph (Adjacency Matrix & List)
 8. Boolean Expression Tree
 9. Expression Tree Operations
10. Heap Stock Prices
11. A* Algorithm
12. N-Queens Problem
13. Logistic Regression
14. SVM Email Classification
15. Pandas Data Processing
''')

    def avl_employee(self):
        print('''\
#include <iostream>
using namespace std;

class Node {
public:
    int id;
    string name;
    Node *left, *right;
    int height;
    Node(int i, string n) {
        id = i;
        name = n;
        left = right = NULL;
        height = 1;
    }
};

int getHeight(Node* root) {
    if (root == NULL) return 0;
    return root->height;
}

int getBalance(Node* root) {
    if (root == NULL) return 0;
    return getHeight(root->left) - getHeight(root->right);
}

Node* rightRotate(Node* y) {
    Node* x = y->left;
    Node* T = x->right;
    x->right = y;
    y->left = T;
    y->height = max(getHeight(y->left), getHeight(y->right)) + 1;
    x->height = max(getHeight(x->left), getHeight(x->right)) + 1;
    return x;
}

Node* leftRotate(Node* x) {
    Node* y = x->right;
    Node* T = y->left;
    y->left = x;
    x->right = T;
    x->height = max(getHeight(x->left), getHeight(x->right)) + 1;
    y->height = max(getHeight(y->left), getHeight(y->right)) + 1;
    return y;
}

Node* insert(Node* root, int id, string name) {
    if (root == NULL) return new Node(id, name);
    if (id < root->id) root->left = insert(root->left, id, name);
    else if (id > root->id) root->right = insert(root->right, id, name);
    else return root; // duplicate

    root->height = 1 + max(getHeight(root->left), getHeight(root->right));
    int bal = getBalance(root);

    if (bal > 1 && id < root->left->id) return rightRotate(root);
    if (bal < -1 && id > root->right->id) return leftRotate(root);
    if (bal > 1 && id > root->left->id) { root->left = leftRotate(root->left); return rightRotate(root); }
    if (bal < -1 && id < root->right->id) { root->right = rightRotate(root->right); return leftRotate(root); }

    return root;
}

Node* minValueNode(Node* node) {
    Node* current = node;
    while (current->left != NULL)
        current = current->left;
    return current;
}

Node* deleteNode(Node* root, int id) {
    if (root == NULL) return root;
    if (id < root->id) root->left = deleteNode(root->left, id);
    else if (id > root->id) root->right = deleteNode(root->right, id);
    else {
        if (root->left == NULL || root->right == NULL) {
            Node* temp = root->left ? root->left : root->right;
            if (temp == NULL) { temp = root; root = NULL; }
            else *root = *temp;
            delete temp;
        } else {
            Node* temp = minValueNode(root->right);
            root->id = temp->id;
            root->name = temp->name;
            root->right = deleteNode(root->right, temp->id);
        }
    }

    if (root == NULL) return root;

    root->height = 1 + max(getHeight(root->left), getHeight(root->right));
    int bal = getBalance(root);

    if (bal > 1 && getBalance(root->left) >= 0) return rightRotate(root);
    if (bal > 1 && getBalance(root->left) < 0) { root->left = leftRotate(root->left); return rightRotate(root); }
    if (bal < -1 && getBalance(root->right) <= 0) return leftRotate(root);
    if (bal < -1 && getBalance(root->right) > 0) { root->right = rightRotate(root->right); return leftRotate(root); }

    return root;
}

void inorder(Node* root) {
    if (root == NULL) return;
    inorder(root->left);
    cout << root->id << " - " << root->name << endl;
    inorder(root->right);
}

void search(Node* root, int id, int &comparisons) {
    if (root == NULL) {
        cout << "Employee not found!\\n";
        return;
    }
    comparisons++;
    if (root->id == id) cout << "Found: " << root->id << " - " << root->name << endl;
    else if (id < root->id) search(root->left, id, comparisons);
    else search(root->right, id, comparisons);
}

int main() {
    Node* root = NULL;
    int ch, id, comparisons;
    string name;

    do {
        cout << "\\n1.Insert\\n2.Search\\n3.Delete\\n4.Display (Inorder)\\n5.Height\\n6.Search Comparisons\\n7.Exit\\nEnter choice: ";
        cin >> ch;
        if (ch == 1) {
            cout << "Enter Employee ID and Name: ";
            cin >> id >> name;
            root = insert(root, id, name);
        } 
        else if (ch == 2) {
            cout << "Enter ID to search: ";
            cin >> id;
            comparisons = 0;
            search(root, id, comparisons);
        } 
        else if (ch == 3) {
            cout << "Enter ID to delete: ";
            cin >> id;
            root = deleteNode(root, id);
        } 
        else if (ch == 4) {
            cout << "\\nEmployee Records (Sorted):\\n";
            inorder(root);
        } 
        else if (ch == 5) {
            cout << "Height of AVL Tree: " << getHeight(root) << endl;
        } 
        else if (ch == 6) {
            cout << "Enter ID to test comparisons: ";
            cin >> id;
            comparisons = 0;
            search(root, id, comparisons);
            cout << "Comparisons made: " << comparisons << endl;
        }
    } while (ch != 7);

    return 0;
}
''')

    def fractional_food(self):
        print('''\
#include <iostream>
using namespace std;

int main() {
    int no_of_packages;
    double truck_capacity;

    cout << "Enter the number of packages: ";
    cin >> no_of_packages;
    cout << "Enter the truck capacity: ";
    cin >> truck_capacity;

    double weight[200], benefit[200], ratio[200];

    // Input weights and benefits
    for (int i = 0; i < no_of_packages; i++) {
        cout << "Enter the weight of package " << i + 1 << ": ";
        cin >> weight[i];
        cout << "Enter the benefit of package " << i + 1 << ": ";
        cin >> benefit[i];
        ratio[i] = benefit[i] / weight[i]; // benefit per weight unit
    }

    // Sort packages based on ratio (descending order)
    for (int i = 0; i < no_of_packages - 1; i++) {
        for (int j = i + 1; j < no_of_packages; j++) {
            if (ratio[i] < ratio[j]) {
                swap(ratio[i], ratio[j]);
                swap(weight[i], weight[j]);
                swap(benefit[i], benefit[j]);
            }
        }
    }

    double total_benefit = 0;
    double total_weight = 0;

    cout << "\\nPackages Selected:\\n";
    for (int i = 0; i < no_of_packages && truck_capacity > 0; i++) {
        double taken_weight = min(truck_capacity, weight[i]);
        double fraction = taken_weight / weight[i];

        total_benefit += benefit[i] * fraction;
        total_weight += taken_weight;
        truck_capacity -= taken_weight;

        cout << "Package " << i + 1
             << " | Fraction taken: " << fraction
             << " | Weight used: " << taken_weight
             << " | Benefit gained: " << benefit[i] * fraction << endl;
    }

    cout << "\\nTotal Truck Weight Used: " << total_weight;
    cout << "\\nTotal Benefit Obtained: " << total_benefit << endl;

    return 0;
}
''')

    def fractional_truck(self):
        print('''\
#include <iostream>
using namespace std;

int main() {
    int no_of_packages;
    double truck_capacity;

    cout << "Enter the number of packages: ";
    cin >> no_of_packages;
    cout << "Enter the truck capacity (in kg): ";
    cin >> truck_capacity;

    double weight[200], benefit[200], ratio[200];

    for (int i = 0; i < no_of_packages; i++) {
        cout << "Enter the weight of package " << i + 1 << ": ";
        cin >> weight[i];
        cout << "Enter the benefit of package " << i + 1 << ": ";
        cin >> benefit[i];
        ratio[i] = benefit[i] / weight[i];
    }

    // Sort by ratio (descending)
    for (int i = 0; i < no_of_packages - 1; i++) {
        for (int j = i + 1; j < no_of_packages; j++) {
            if (ratio[i] < ratio[j]) {
                swap(weight[i], weight[j]);
                swap(benefit[i], benefit[j]);
                swap(ratio[i], ratio[j]);
            }
        }
    }

    double totalBenefit = 0;

    for (int i = 0; i < no_of_packages && truck_capacity > 0; i++) {
        double taken_weight = min(truck_capacity, weight[i]);
        totalBenefit += ratio[i] * taken_weight;

        cout << "Package " << i + 1 
             << ": Weight taken: " << taken_weight 
             << ", Fraction: " << taken_weight / weight[i] 
             << ", Benefit: " << ratio[i] * taken_weight << endl;

        truck_capacity -= taken_weight;
    }

    cout << "\\nTotal Truck Weight Used: " << (truck_capacity <= 0 ? "Full" : "Partially Filled") << endl;
    cout << "Total Benefit Obtained: " << totalBenefit << endl;

    return 0;
}
''')

    def knapsack_file(self):
        print('''\
#include <iostream>
using namespace std;

int main() {
    // Predefined number of files and capacity
    int fileCount = 4;
    int capacity = 7;

    // Predefined sizes and importance values
    int size[] = {1, 3, 4, 5};
    int importance[] = {2, 4, 5, 7};

    int dp[5][8] = {0}; // dp[fileCount+1][capacity+1]

    // Build DP table
    for (int i = 1; i <= fileCount; i++) {
        for (int j = 1; j <= capacity; j++) {
            if (size[i - 1] <= j)
                dp[i][j] = max(importance[i - 1] + dp[i - 1][j - size[i - 1]], dp[i - 1][j]);
            else
                dp[i][j] = dp[i - 1][j];
        }
    }

    // Display results
    cout << "Maximum Total Importance: " << dp[fileCount][capacity] << endl;

    cout << "\\nSelected Files:\\n";
    int remaining = capacity;
    for (int i = fileCount; i > 0; i--) {
        if (dp[i][remaining] != dp[i - 1][remaining]) {
            cout << "File " << i << " (Size: " << size[i - 1]
                 << ", Importance: " << importance[i - 1] << ")\\n";
            remaining -= size[i - 1];
        }
    }

    return 0;
}
''')

    def maxmin_heap(self):
        print('''\
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

class JobHeap {
    vector<int> maxHeap; // For highest priority jobs
    vector<int> minHeap; // For lowest priority jobs

public:
    // Insert new job
    void insert(int priority) {
        maxHeap.push_back(priority);
        push_heap(maxHeap.begin(), maxHeap.end()); // Max heap by default

        minHeap.push_back(priority);
        push_heap(minHeap.begin(), minHeap.end(), greater<int>()); // Min heap
        cout << "Job inserted with priority " << priority << endl;
    }

    // Find highest priority job
    void findMax() {
        if (maxHeap.empty())
            cout << "No jobs available.\\n";
        else
            cout << "Highest priority job: " << maxHeap.front() << endl;
    }

    // Find lowest priority job
    void findMin() {
        if (minHeap.empty())
            cout << "No jobs available.\\n";
        else
            cout << "Lowest priority job: " << minHeap.front() << endl;
    }

    // Delete highest priority job
    void deleteMax() {
        if (maxHeap.empty()) {
            cout << "No jobs to delete.\\n";
            return;
        }
        cout << "Deleting highest priority job: " << maxHeap.front() << endl;
        pop_heap(maxHeap.begin(), maxHeap.end());
        maxHeap.pop_back();

        // Rebuild minHeap since it also changes
        minHeap.clear();
        for (int p : maxHeap) {
            minHeap.push_back(p);
        }
        make_heap(minHeap.begin(), minHeap.end(), greater<int>());
    }

    // Display all jobs in order
    void display() {
        if (maxHeap.empty()) {
            cout << "No jobs to display.\\n";
            return;
        }
        cout << "Jobs in order of priority (high → low): ";
        vector<int> temp = maxHeap;
        sort(temp.begin(), temp.end(), greater<int>());
        for (int p : temp)
            cout << p << " ";
        cout << endl;
    }
};

int main() {
    JobHeap h;
    int choice, priority;

    do {
        cout << "\\n--- Job Priority Menu ---\\n";
        cout << "1. Insert new job\\n";
        cout << "2. Find highest and lowest priority\\n";
        cout << "3. Delete highest priority job\\n";
        cout << "4. Display all jobs\\n";
        cout << "5. Exit\\n";
        cout << "Enter choice: ";
        cin >> choice;

        switch (choice) {
        case 1:
            cout << "Enter job priority: ";
            cin >> priority;
            h.insert(priority);
            break;
        case 2:
            h.findMax();
            h.findMin();
            break;
        case 3:
            h.deleteMax();
            break;
        case 4:
            h.display();
            break;
        case 5:
            cout << "Exiting...\\n";
            break;
        default:
            cout << "Invalid choice!\\n";
        }
    } while (choice != 5);

    return 0;
}
''')

    def flight(self):
        print('''\
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cout << "Enter number of airlines: ";
    cin >> n;
    vector<vector<int>> adjMatrix(n, vector<int>(n, 0));
    vector<vector<int>> adjList(n);
    int e;
    cout << "Enter number of partnerships: ";
    cin >> e;
    cout << "Enter partnerships (airline1 airline2 weight):\\n";
    for (int i = 0; i < e; i++) {
        int a, b, w;
        cin >> a >> b >> w;
        adjMatrix[a][b] = w;
        adjMatrix[b][a] = w;
        adjList[b].push_back(a);
    }
   
    int choice;
    do {
        cout << "\\nMenu:\\n";
        cout << "1. Check if two airlines have partnership\\n";
        cout << "2. display all airlines connected to a given air line\\n";
        cout << "3. Exit\\n";
        cout << "Enter your choice";
        cin >> choice;
        if (choice == 1) {
        int a,b;
        cout << "Enter the two airlines to check";
        cin >> a >> b;
        if (adjMatrix[a][b] != 0)
        cout << "Airlines" << a << "and airlines" << b
             << " have a partnership (weight: " << adjMatrix[a][b] << ")\\n";
        else
                cout << "No partnership found.\\n";
        }
        else if (choice == 2){
            int a;
            cout << "Enter airline number:";
            cin >> a;
            cout << "Airlne connected to airline " << a << ":";
            for (int partner : adjList[a]){
                cout << partner << " ";
            }
            cout << endl;
        }
    } while (choice != 3);

    return 0;
}
''')

    def boolean_expression(self):
        print('''\
#include <iostream>
#include <stack>
#include <cctype>
using namespace std;

struct Node {
    char data;
    Node *left, *right;
    Node(char val) : data(val), left(NULL), right(NULL) {}
};

// Build expression tree from prefix expression
Node* createTree(string exp) {
    stack<Node*> st;
    for (int i = exp.size() - 1; i >= 0; i--) {
        char c = exp[i];
        Node* node = new Node(c);

        if (isalpha(c)) st.push(node);
        else if (c == '!' && !st.empty()) { // Unary operator
            node->right = st.top();
            st.pop();
            st.push(node);
        }
        else { // Binary operator
            if (st.size() < 2) {
                cout << "Invalid expression!\\n";
                return NULL;
            }
            node->left = st.top(); st.pop();
            node->right = st.top(); st.pop();
            st.push(node);
        }
    }
    return st.empty() ? NULL : st.top();
}

// Traversals
void inorder(Node* root) {
    if (!root) return;
    inorder(root->left);
    cout << root->data << " ";
    inorder(root->right);
}
void preorder(Node* root) {
    if (!root) return;
    cout << root->data << " ";
    preorder(root->left);
    preorder(root->right);
}
void postorder(Node* root) {
    if (!root) return;
    postorder(root->left);
    postorder(root->right);
    cout << root->data << " ";
}

// Swap subtrees
void swapTree(Node* root) {
    if (!root) return;
    swap(root->left, root->right);
    swapTree(root->left);
    swapTree(root->right);
}

int main() {
    string exp;
    cout << "Enter prefix Boolean expression (e.g. |&AB!C): ";
    cin >> exp;

    Node* root = createTree(exp);
    if (!root) return 0;

    cout << "\\nInorder: "; inorder(root);
    cout << "\\nPreorder: "; preorder(root);
    cout << "\\nPostorder: "; postorder(root);

    cout << "\\n\\nAfter swapping left and right subtrees:";
    swapTree(root);
    cout << "\\nInorder: "; inorder(root);
    cout << "\\nPreorder: "; preorder(root);
    cout << "\\nPostorder: "; postorder(root);
    cout << endl;

    return 0;
}
''')
