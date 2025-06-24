#!/usr/bin/env python3
"""
Crack Hash Silverh
Autor: [Silver H]
"""

import base64
import itertools
import argparse
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração de cores para melhor visualização
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def banner():
    print(f"""{bcolors.HEADER}
██████  ███████ ██████  █████   ██████ ██   ██ 
██   ██ ██      ██   ██ ██   ██ ██      ██  ██  
██████  █████   ██████  ███████ ██      █████   
██   ██ ██      ██   ██ ██   ██ ██      ██  ██  
██   ██ ███████ ██   ██ ██   ██  ██████ ██   ██ 
------------------------------------------------
Quebra - Crack Avancada de Hashes Base64 {bcolors.ENDC}""")

def generate_combinations(charset, min_len, max_len):
    """Gera todas as combinações possíveis de caracteres"""
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)

def try_decoding(hash_base64, candidate):
    """Tenta decodificar a hash com o candidato atual"""
    try:
        decoded = base64.b64decode(candidate.encode()).decode()
        if decoded == hash_base64:
            return candidate, decoded
    except:
        pass
    return None

def dictionary_attack(hash_base64, wordlist):
    """Ataque usando dicionário de palavras"""
    print(f"{bcolors.OKBLUE}[*] Iniciando ataque com dicionário...{bcolors.ENDC}")
    try:
        with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f]
    except Exception as e:
        print(f"{bcolors.FAIL}[!] Erro ao ler wordlist: {str(e)}{bcolors.ENDC}")
        return None

    with ThreadPoolExecutor(max_workers=os.cpu_count() * 4) as executor:
        futures = []
        for word in words:
            # Tenta variações comuns
            variations = [
                word,
                word.lower(),
                word.upper(),
                word.capitalize(),
                word + "123",
                word + "!",
                "123" + word
            ]
            
            for variant in variations:
                futures.append(executor.submit(try_decoding, hash_base64, variant))
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                return result
    
    return None

def brute_force_attack(hash_base64, charset, min_len, max_len):
    """Ataque de força bruta pura"""
    print(f"{bcolors.OKBLUE}[*] Iniciando força bruta ({min_len}-{max_len} caracteres)...{bcolors.ENDC}")
    total_combinations = sum(len(charset)**n for n in range(min_len, max_len + 1))
    print(f"{bcolors.WARNING}[*] Espaço de busca: {total_combinations:,} combinações{bcolors.ENDC}")
    
    count = 0
    start_time = time.time()
    
    for candidate in generate_combinations(charset, min_len, max_len):
        result = try_decoding(hash_base64, candidate)
        count += 1
        
        # Atualização de progresso
        if count % 100000 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            print(f"{bcolors.OKGREEN}[*] Testadas: {count:,} | Velocidade: {rate:,.0f} hashes/seg{bcolors.ENDC}")
        
        if result:
            return result
    
    return None

def analyze_hash(hash_base64):
    """Analisa a hash para determinar características"""
    print(f"\n{bcolors.HEADER}=== ANÁLISE DA HASH ==={bcolors.ENDC}")
    print(f"Tamanho da hash: {len(hash_base64)} caracteres")
    
    char_types = {
        'Letras minúsculas': sum(c.islower() for c in hash_base64),
        'Letras maiúsculas': sum(c.isupper() for c in hash_base64),
        'Dígitos': sum(c.isdigit() for c in hash_base64),
        'Caracteres especiais': sum(not c.isalnum() for c in hash_base64)
    }
    
    print("Composição:")
    for k, v in char_types.items():
        print(f"- {k}: {v} ({v/len(hash_base64):.1%})")
    
    # Sugestão de ataque baseada na análise
    if char_types['Caracteres especiais'] > 2:
        print(f"{bcolors.WARNING}[*] Sugestão: Priorize ataque com dicionário{bcolors.ENDC}")
    else:
        print(f"{bcolors.WARNING}[*] Sugestão: Priorize força bruta com charset reduzido{bcolors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Ferramenta para Quebra de Hashes Base64 - TCC")
    parser.add_argument("hash", help="Hash Base64 para decodificar")
    parser.add_argument("-w", "--wordlist", help="Arquivo com wordlist para ataque de dicionário")
    parser.add_argument("-b", "--brute-force", action="store_true", help="Usar força bruta")
    parser.add_argument("-c", "--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
                        help="Conjunto de caracteres para força bruta")
    parser.add_argument("-min", "--min-length", type=int, default=4, help="Comprimento mínimo para força bruta")
    parser.add_argument("-max", "--max-length", type=int, default=8, help="Comprimento máximo para força bruta")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Número de threads paralelas")
    
    args = parser.parse_args()
    
    banner()
    analyze_hash(args.hash)
    
    result = None
    start_time = time.time()
    
    # Estratégia combinada: primeiro dicionário, depois força bruta
    if args.wordlist:
        result = dictionary_attack(args.hash, args.wordlist)
    
    if not result and args.brute_force:
        result = brute_force_attack(
            args.hash,
            args.charset,
            args.min_length,
            args.max_length
        )
    
    elapsed = time.time() - start_time
    
    if result:
        candidate, decoded = result
        print(f"\n{bcolors.OKGREEN}[+] SUCESSO! Hash decodificada{bcolors.ENDC}")
        print(f"{bcolors.BOLD}Chave original: {candidate}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}Conteúdo decodificado: {decoded}{bcolors.ENDC}")
        print(f"Tempo total: {elapsed:.2f} segundos")
    else:
        print(f"\n{bcolors.FAIL}[-] FALHA! Hash não decodificada{bcolors.ENDC}")
        print("Tente:")
        print("- Ampliar o charset (-c)")
        print("- Aumentar o tamanho máximo (-max)")
        print("- Usar uma wordlist mais completa (-w)")

if __name__ == "__main__":
    main()