style1 = """body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    display: flex;
    background-color: #f8f9fa;
}

.sidebar {
    width: 300px;
    height: 100vh;
    overflow-y: auto;
    background-color: #ffffff;
    padding: 30px;
    position: fixed;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}

.main-content {
    margin-left: 360px;
    padding: 50px;
    max-width: 800px;
    background-color: #ffffff;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    min-height: 100vh;
}

.sidebar ul {
    list-style-type: none;
    padding-left: 0;
}

.sidebar ul ul {
    padding-left: 20px;
}

.sidebar a {
    text-decoration: none;
    color: #495057;
    display: block;
    padding: 8px 0;
    transition: all 0.3s ease;
    font-size: 15px;
}

.sidebar a:hover {
    color: #007bff;
    padding-left: 5px;
}

.sidebar .active {
    font-weight: 600;
    color: #007bff;
}

h1,
h2,
h3,
h4 {
    color: #212529;
    margin-top: 0;
    font-weight: 600;
}

h1 {
    font-size: 32px;
    border-bottom: 2px solid #007bff;
    padding-bottom: 15px;
    margin-bottom: 30px;
}

h2 {
    font-size: 24px;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
    margin-top: 40px;
    margin-bottom: 20px;
}

h3 {
    font-size: 20px;
    margin-top: 30px;
}

h4 {
    font-size: 18px;
    margin-top: 25px;
}

.text {
    margin-bottom: 20px;
    font-size: 16px;
    color: #495057;
}

section {
    margin-bottom: 40px;
}

/* New styles for nested sections */
section section {
    margin-left: 20px;
    border-left: 2px solid #e9ecef;
    padding-left: 20px;
}

section section section {
    margin-left: 15px;
}

section section section section {
    margin-left: 10px;
}

.sidebar-title {
    font-size: 24px;
    font-weight: 600;
    color: #212529;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #007bff;
}

@media (max-width: 1200px) {
    .sidebar {
        width: 250px;
    }

    .main-content {
        margin-left: 300px;
    }
}

@media (max-width: 992px) {
    body {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        height: auto;
        position: static;
        padding: 20px;
    }

    .main-content {
        margin-left: 0;
        padding: 30px;
    }
}"""

style2 = """
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    display: flex;
}

/* Sidebar styles */
.sidebar {
    width: 250px;
    height: 100vh;
    background-color: #f4f4f4;
    padding: 20px;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    position: fixed;
}

.sidebar-title {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 15px;
    color: #2c3e50;
}

.sidebar ul {
    list-style-type: none;
    padding-left: 15px;
}

.sidebar li {
    margin-bottom: 10px;
}

.sidebar a {
    text-decoration: none;
    color: #34495e;
    transition: color 0.3s ease;
}

.sidebar a:hover {
    color: #3498db;
}

/* Main content styles */
.main-content {
    margin-left: 250px;
    padding: 40px;
    max-width: 800px;
}

/* Section styles */
section {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease;
}

section:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Heading styles */
h1,
h2,
h3,
h4 {
    color: #2c3e50;
    margin-top: 0;
}

h1 {
    font-size: 2em;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

h2 {
    font-size: 1.75em;
    border-bottom: 1px solid #3498db;
    padding-bottom: 8px;
}

h3 {
    font-size: 1.5em;
    color: #34495e;
}

h4 {
    font-size: 1.25em;
    color: #7f8c8d;
}

/* Nested section styles */
section section {
    margin-left: 20px;
    border-left: 3px solid #3498db;
}

/* Text styles */
.text {
    font-size: 1em;
    color: #555;
}

/* Responsive design */
@media (max-width: 768px) {
    body {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        height: auto;
        position: static;
    }

    .main-content {
        margin-left: 0;
        padding: 20px;
    }
}"""