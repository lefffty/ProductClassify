class ClassStructQueries:
    FIND_GR_GR = "SELECT * FROM find_gr_gr(%s);"
    GET_TERMINAL_CLASSES = "SELECT * FROM get_terminal_classes(%s);"
    DELETE_CLASS_AND_DESCENDANTS = "SELECT * FROM delete_class_and_descendants(%s);"
    CHECK_CYCLE = "SELECT * FROM check_class_struct_cycles(%s, %s);"
