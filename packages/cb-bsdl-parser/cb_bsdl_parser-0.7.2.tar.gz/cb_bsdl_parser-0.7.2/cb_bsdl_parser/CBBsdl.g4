grammar CBBsdl;

options {
    tokenVocab = CBBsdlLexer;
}

// parser rules

bsdl
    :
    entity
    comment*
    ;


// entity
entity
    : ENTITY entity_name IS
    body
    END
    entity_name
    SEMICOLON
    ;

entity_name
    : identifier
    ;


body
    :
    (
      (
        generic_phys_pin_map
      | port_dec
      | pin_map
      | attr_bsr_len
      | attr_bsr
      | undef_part
      )
    )*
    ;


// pin mapping
generic_phys_pin_map
    :
    GENERIC
    BRACKET_OPEN
    PHYSICAL_PIN_MAP
    COLON
    STRING
    EQUALS
    QUOTES
    phys_pin_map_name
    QUOTES
    BRACKET_CLOSE
    SEMICOLON
    ;

phys_pin_map_name
    : identifier
    ;


// attribute boundary scan register length
attr_bsr_len
    :
    ATTRIBUTE
    BS_LEN
    OF
    entity_name
    COLON
    ENTITY
    IS
    bsr_len
    SEMICOLON
    ;

bsr_len
    : number
    ;


// port declaration
port_dec
    :
    PORT
    BRACKET_OPEN
    (port_def)+
    BRACKET_CLOSE
    SEMICOLON
    ;

port_def
    :
    (port_name COMMA?)+
    COLON
    port_function
    port_type
    SEMICOLON?
    ;

port_name
    :
    identifier
    ;

port_function
    :
    (INOUT | IN | OUT | LINKAGE)
    ;


port_type
    :
      bit
    | bit_vector
    | ID
    ;

bit
    :
    BIT
    ;

bit_vector
    :
    BIT_VECTOR
    BRACKET_OPEN
    bit_range
    BRACKET_CLOSE
    ;

pin_map
    :
    CONSTANT
    phys_pin_map_name
    COLON
    PIN_MAP_STRING
    EQUALS
    (pin_def)+
    SEMICOLON
    ;


pin_def
    :
    QUOTES?
    port_name
    COLON
    (pin_num | pin_num_arr)
    COMMA?
    QUOTES?
    AMPERSAND?
    ;

pin_num
    :
    (identifier | number)
    ;

pin_num_arr
    :
    BRACKET_OPEN
    (pin_num COMMA?)+
    BRACKET_CLOSE
    ;


// attribute BOUNDARY_REGISTER
attr_bsr
    :
    ATTRIBUTE
    BS_REG
    OF
    entity_name
    COLON
    ENTITY
    IS
    (bsr_def)+
    SEMICOLON
    ;

bsr_def
    :
    QUOTES
    data_cell
    BRACKET_OPEN
    (bsr_cell0 | bsr_cell1)
    BRACKET_CLOSE
    COMMA?
    QUOTES
    AMPERSAND?
    ;

data_cell
    :
    INTEGER
    ;

bsr_cell0
    :
    cell_type
    COMMA
    (cell_desc | ASTERISK)
    COMMA
    cell_func
    COMMA
    cell_val
    ;

bsr_cell1
    :
    cell_type
    COMMA
    cell_desc
    COMMA
    cell_func
    COMMA
    cell_val
    COMMA
    ctrl_cell
    COMMA
    disval
    COMMA
    identifier
    ;

cell_type
    :
    ID
    ;

cell_desc
    :
    (
      identifier
    | BRACKET_OPEN
    | number
    | BRACKET_CLOSE
    )*
    ;

cell_func
    :
    ID
    ;

cell_val
    :
    (identifier | number)
    ;

ctrl_cell
    :
    number
    ;

disval
    :
    number
    ;

bit_range:
    INTEGER TO INTEGER |
    INTEGER DOWNTO INTEGER
    ;

undef_part
    :
    (~SEMICOLON)+
    SEMICOLON
    ;

// ---------------
number
    : INTEGER
    ;



identifier
    : ID
    ;


comment
    : COMMENT
    ;