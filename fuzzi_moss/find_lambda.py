import ast


def find_candidate_object(offset, source_line):
    start = source_line.index('lambda', offset)-1
    end = start + 7

    while end <= len(source_line):
        try:
            candidate_source = source_line[start:end]
            return compile(candidate_source, filename='blank', mode='exec').co_consts[0], candidate_source, end
        except SyntaxError:
            end += 1


def find_lambda_ast(source_line, lambda_object):
    result = list()
    offset = 0
    while True:
        candidate_object, candidate_source, offset = find_candidate_object(offset, source_line)
        if candidate_object.co_code == lambda_object.func_code.co_code:
            return ast.parse(candidate_source).body[0]