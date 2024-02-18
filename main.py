from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
import re

compiler = Tk()
compiler.title('Compilador Ruby/Julia')
file_path = ''


def set_file_path(path):
    global file_path
    file_path = path


class SemanticsAnalyzer:
    def __init__(self):
        self.symbol_table = {'global': {}}
        self.current_scope = 'global'
        self.errors = []  # Lista para almacenar mensajes de error semántico

    def analyze_semantics(self, code, language):
        if language == 'ruby':
            self.analyze_ruby_semantics(code)
        elif language == 'julia':
            self.analyze_julia_semantics(code)

    def analyze_ruby_semantics(self, code):
        # Verificar la correcta definición y uso de variables
        variables = re.findall(r'\b(\w+)\s*=\s*(.+?)\b', code)
        for variable, value in variables:
            if variable in self.symbol_table[self.current_scope]:
                self.errors.append(f"Advertencia: Variable '{variable}' ya definida en el ámbito actual.")
            else:
                self.symbol_table[self.current_scope][variable] = value

        # Verificar llamadas a funciones y sus argumentos
        function_calls = re.findall(r'\b(\w+)\((.*?)\)\b', code)
        for function, arguments in function_calls:
            if function not in self.symbol_table[self.current_scope]:
                self.errors.append(f"Error: Función '{function}' no definida.")
            else:
                # Verificar la correspondencia entre los argumentos de la función y sus parámetros
                expected_parameters = re.findall(r'\bdef\s+%s\((.*?)\)' % function, code)
                if expected_parameters:
                    expected_parameters = expected_parameters[0].split(',')
                    provided_arguments = arguments.split(',')
                    if len(expected_parameters) != len(provided_arguments):
                        self.errors.append(f"Error: Número incorrecto de argumentos para la función '{function}'.")

    def analyze_julia_semantics(self, code):
        # Verificar la correcta definición y uso de variables en Julia
        variables = re.findall(r'\b(\w+)\s*=\s*(.+?)\b', code)
        for variable, value in variables:
            if variable in self.symbol_table[self.current_scope]:
                self.errors.append(f"Advertencia: Variable '{variable}' ya definida en el ámbito actual.")
            else:
                self.symbol_table[self.current_scope][variable] = value

        # Verificar llamadas a funciones y sus argumentos en Julia
        function_calls = re.findall(r'\b(\w+)\((.*?)\)\b', code)
        for function, arguments in function_calls:
            if function not in self.symbol_table[self.current_scope]:
                self.errors.append(f"Error: Función '{function}' no definida.")
            else:
                # Verificar la correspondencia entre los argumentos de la función y sus parámetros
                expected_parameters = re.findall(r'\bfunction\s+%s\((.*?)\)' % function, code)
                if expected_parameters:
                    expected_parameters = expected_parameters[0].split(',')
                    provided_arguments = arguments.split(',')
                    if len(expected_parameters) != len(provided_arguments):
                        self.errors.append(f"Error: Número incorrecto de argumentos para la función '{function}'.")

    def report_errors(self):
        return "\n".join(self.errors)


def detect_language(content):
    patterns = {
        'julia': r'\b(julia|function|using|global|let|struct|importall|println)\b',
        'ruby': r'\b(ruby|require|puts|def|alias|class|elsif|module)\b'
    }

    detected_language = None

    for language, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            detected_language = language
            break

    return detected_language


def open_file():
    path = askopenfilename(filetypes=[('Julia/Ruby Files', '*.jl .rb')])
    with open(path, 'r') as file:
        code = file.read()
        code_output.delete("1.0", END)
        detected_language = detect_language(code)
        code_output.insert("1.0", detected_language)
        editor.delete('1.0', END)
        editor.insert('1.0', code)
        set_file_path(path)

        semantic_analyzer = SemanticsAnalyzer()
        semantic_analyzer.analyze_semantics(code, detected_language)

        error_message = semantic_analyzer.report_errors()
        if error_message:
            code_output.insert(END, f"\n\nErrores Semánticos:\n{error_message}")
        else:
            code_output.insert(END, "\n\nNo hay errores semánticos.")


def save_as():
    if file_path == '':
        path = asksaveasfilename(filetypes=[('Python Files', '*.py')])
    else:
        path = file_path
    with open(path, 'w') as file:
        code = editor.get('1.0', END)
        file.write(code)
        set_file_path(path)


menu_bar = Menu(compiler)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label='Open', command=open_file)
file_menu.add_command(label='Save', command=save_as)
file_menu.add_command(label='Save As', command=save_as)
file_menu.add_command(label='Exit', command=exit)
menu_bar.add_cascade(label='File', menu=file_menu)

run_bar = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Run', menu=run_bar)

compiler.config(menu=menu_bar)

editor = Text()
editor.pack()

code_output = Text(height=10)
code_output.pack()

compiler.mainloop()