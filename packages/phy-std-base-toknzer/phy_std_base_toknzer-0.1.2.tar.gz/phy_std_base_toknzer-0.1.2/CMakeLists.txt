cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Development.Module
  REQUIRED)

python_add_library(
  _tokenize MODULE 
  src/phy_std_base_toknzer/_tokenize/_tokenize_module.c 
  src/phy_std_base_toknzer/_tokenize/_tokenize.c
  src/phy_std_base_toknzer/_tokenize/lexer/buffer.c
  src/phy_std_base_toknzer/_tokenize/lexer/lexer.c
  src/phy_std_base_toknzer/_tokenize/lexer/state.c
  src/phy_std_base_toknzer/_tokenize/tokenizer/helpers.c
  src/phy_std_base_toknzer/_tokenize/tokenizer/readline_tokenizer.c
  src/phy_std_base_toknzer/_tokenize/tokenizer/string_tokenizer.c
  src/phy_std_base_toknzer/_tokenize/tokenizer/utf8_tokenizer.c
  WITH_SOABI
)

install(TARGETS _tokenize DESTINATION phy_std_base_toknzer)
install(
  FILES src/phy_std_base_toknzer/__init__.py
        src/phy_std_base_toknzer/_tokenize.pyi
        src/phy_std_base_toknzer/tok_def.py
  DESTINATION phy_std_base_toknzer
)
