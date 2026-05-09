
rule test:
    output: 'test.txt'
    shell: 'echo hello > {output}'

