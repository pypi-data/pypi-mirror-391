# pylpex/typesystem.py
import re
from typing import List, Optional, Union
from enum import Enum

class BaseType(Enum):
    # Data types
    NONE = "null"
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "bool"
    LIST = "list"
    DICTIONARY = "dict"
    CALLABLE = "callable"
    # Type constructors
    UNION = "union"
    # OPTIONAL = "optional"
    ARGS = "args"
    VARIADIC = "variadic" # for variadic arguments *args
    KW_VARIADIC = "kw_variadic" # for variadic keyword arguments **kwargs
    # Special types
    ANY = "any"  # non strict typing

class TypeInfo:
    """Représente un type dans le système Pylpex."""
    def __init__(self, base: BaseType, subtypes: Optional[Union['TypeInfo', List['TypeInfo']]] = None):
        self.base = base
        # subtypes est soit None, soit un TypeInfo unique, soit une liste de TypeInfo
        if isinstance(subtypes, TypeInfo):
            self.subtypes = [subtypes]
        elif isinstance(subtypes, list):
            self.subtypes = subtypes
        else:
            self.subtypes = None

    def __repr__(self):
        if self.subtypes:
            inner = ", ".join(repr(s) for s in self.subtypes)
            return f"{self.base.value}[{inner}]"
        return self.base.value
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        
        # Les bases doivent être identiques
        if self.base != other.base:
            return False
        
        # Cas sans sous-types
        if self.subtypes is None and other.subtypes is None:
            return True
        
        if self.subtypes is None or other.subtypes is None:
            return False
        
        # Pour les unions, l'ordre n'a pas d'importance
        if self.base == BaseType.UNION:
            # Vérifier que chaque type de self est dans other et vice-versa
            if len(self.subtypes) != len(other.subtypes):
                return False
            
            # Créer des ensembles pour comparer sans tenir compte de l'ordre
            # On ne peut pas utiliser set() directement car TypeInfo n'est pas hashable
            for s_type in self.subtypes:
                if not any(s_type == o_type for o_type in other.subtypes):
                    return False
            
            for o_type in other.subtypes:
                if not any(o_type == s_type for s_type in self.subtypes):
                    return False
            
            return True
        
        return False
    
    def __le__(self, other: 'TypeInfo') -> bool:
        """
        Vérifie si self est inclus dans other (self <= other).
        Retourne True si une valeur de type self peut être utilisée là où other est attendu.
        """
        if not isinstance(other, TypeInfo):
            return False
        
        # ANY accepte tout
        if other.base == BaseType.ANY:
            return True
        
        # Rien n'est inclus dans ANY sauf ANY lui-même
        if self.base == BaseType.ANY:
            return other.base == BaseType.ANY
        
        # Cas des unions : self <= union[A, B, ...] si self <= A ou self <= B ou ...
        if other.base == BaseType.UNION and other.subtypes:
            return any(self <= t for t in other.subtypes)
        
        # Cas où self est une union : union[A, B] <= other si A <= other et B <= other
        if self.base == BaseType.UNION and self.subtypes:
            return all(t <= other for t in self.subtypes)
        
        # Les bases doivent correspondre pour les types non-union
        if self.base != other.base:
            return False
        
        # Types sans sous-types : égalité stricte
        if self.subtypes is None and other.subtypes is None:
            return True
        
        # Si other n'a pas de sous-types mais self en a, pas d'inclusion
        if self.subtypes is not None and other.subtypes is None:
            return False
        
        # Si self n'a pas de sous-types mais other en a, pas d'inclusion non plus
        if self.subtypes is None and other.subtypes is not None:
            return False
        
        # Cas des listes et dictionnaires : list[int] <= list[union[int, float]]
        if self.base in (BaseType.LIST, BaseType.DICTIONARY):
            if len(self.subtypes) != len(other.subtypes):
                return False
            return all(s <= o for s, o in zip(self.subtypes, other.subtypes))
        
        # Cas des callables : callable[[args], ret] <= callable[[args'], ret']
        # Un callable est inclus si ses arguments sont plus généraux et son retour plus spécifique
        if self.base == BaseType.CALLABLE:
            if len(self.subtypes) != 2 or len(other.subtypes) != 2:
                return False
            
            self_args, self_ret = self.subtypes
            other_args, other_ret = other.subtypes
            
            # Contravariance pour les arguments : other_args <= self_args
            # Covariance pour le retour : self_ret <= other_ret
            args_compatible = other_args <= self_args if other_args.base == BaseType.ARGS else False
            ret_compatible = self_ret <= other_ret
            
            return args_compatible and ret_compatible
        
        # Cas des args : args[int, string] <= args[union[int, float], any]
        if self.base == BaseType.ARGS:
            if len(self.subtypes) != len(other.subtypes):
                return False
            return all(s <= o for s, o in zip(self.subtypes, other.subtypes))
        
        # Par défaut, égalité stricte des sous-types
        return self.subtypes == other.subtypes

    # @classmethod
    # def from_string(cls, type_str: str) -> 'TypeInfo':
    #     """
    #     Parse une chaîne de caractères pour créer un TypeInfo.
    #     Exemples:
    #     - "int" -> TypeInfo(INTEGER)
    #     - "list[int]" -> TypeInfo(LIST, [TypeInfo(INTEGER)])
    #     - "union[int, string]" -> TypeInfo(UNION, [TypeInfo(INTEGER), TypeInfo(STRING)])
    #     - "callable[[int, string], bool]" -> callable avec args et return type
    #     """
    #     type_str = type_str.strip()
        
    #     # Essayer de trouver le type de base et les sous-types entre crochets
    #     match = re.match(r'^(\w+)(?:\[(.*)\])?$', type_str)
    #     if not match:
    #         raise ValueError(f"Format de type invalide: {type_str}")
        
    #     base_str, subtypes_str = match.groups()

    #     print(f"base_str: {base_str}, subtypes_str: {subtypes_str}")
        
    #     # Trouver le BaseType correspondant
    #     base_type = None
    #     for bt in BaseType:
    #         if bt.value == base_str:
    #             base_type = bt
    #             break
        
    #     if base_type is None:
    #         raise ValueError(f"Type de base inconnu: {base_str}")
        
    #     # Si pas de sous-types, retourner directement
    #     if not subtypes_str:
    #         return cls(base_type)
        
    #     # Parser les sous-types
    #     subtypes = cls._parse_subtypes(subtypes_str)
        
    #     # Cas spécial pour callable: callable[[arg1, arg2], return_type]
    #     if base_type == BaseType.CALLABLE:
    #         if len(subtypes) != 2:
    #             raise ValueError("callable doit avoir exactement 2 sous-types: [[args], return_type]")
    #         # Le premier sous-type doit être une liste d'arguments
    #         if not isinstance(subtypes[0], list):
    #             raise ValueError("Le premier sous-type de callable doit être une liste d'arguments")
    #         args_type = cls(BaseType.ARGS, subtypes[0])
    #         return cls(base_type, [args_type, subtypes[1]])
        
    #     return cls(base_type, subtypes)
    
    # @classmethod
    # def _parse_subtypes(cls, subtypes_str: str) -> List['TypeInfo']:
    #     """
    #     Parse une chaîne de sous-types séparés par des virgules.
    #     Gère les crochets imbriqués.
    #     """
    #     subtypes = []
    #     current = ""
    #     depth = 0
    #     in_brackets = False
        
    #     i = 0
    #     while i < len(subtypes_str):
    #         char = subtypes_str[i]
            
    #         if char == '[':
    #             # Début d'une liste pour callable
    #             if depth == 0 and not in_brackets:
    #                 in_brackets = True
    #                 bracket_content = ""
    #                 i += 1
    #                 bracket_depth = 1
    #                 while i < len(subtypes_str) and bracket_depth > 0:
    #                     if subtypes_str[i] == '[':
    #                         bracket_depth += 1
    #                     elif subtypes_str[i] == ']':
    #                         bracket_depth -= 1
    #                         if bracket_depth == 0:
    #                             break
    #                     bracket_content += subtypes_str[i]
    #                     i += 1
    #                 # Parser le contenu entre crochets comme une liste de types
    #                 subtypes.append(cls._parse_subtypes(bracket_content))
    #                 in_brackets = False
    #                 i += 1
    #                 continue
    #             else:
    #                 depth += 1
    #                 current += char
    #         elif char == ']':
    #             depth -= 1
    #             current += char
    #         elif char == ',' and depth == 0 and not in_brackets:
    #             # Séparateur au niveau supérieur
    #             if current.strip():
    #                 subtypes.append(cls.from_string(current.strip()))
    #             current = ""
    #             i += 1
    #             continue
    #         else:
    #             current += char
            
    #         i += 1
        
    #     # Ajouter le dernier sous-type
    #     if current.strip():
    #         subtypes.append(cls.from_string(current.strip()))
        
    #     return subtypes


    @classmethod
    def union(cls, *types: 'TypeInfo') -> 'TypeInfo':
        """Crée un type union simplifié à partir de plusieurs TypeInfo."""
        flattened = []

        for t in types:
            if t is None:
                continue
            # Aplatir les unions imbriquées : union[union[int, string], bool] -> [int, string, bool]
            if t.base == BaseType.UNION and t.subtypes:
                flattened.extend(t.subtypes)
            else:
                flattened.append(t)

        # Supprimer les doublons (en comparant base + sous-types)
        unique_types = []
        for t in flattened:
            if not any(t == u for u in unique_types):
                unique_types.append(t)

        # Si vide, renvoyer ANY
        if not unique_types:
            return cls(BaseType.ANY)

        # Si un seul type, inutile d'avoir UNION
        if len(unique_types) == 1:
            return unique_types[0]

        # Si tous les types sont égaux → pas besoin d’union non plus
        if all(t == unique_types[0] for t in unique_types):
            return unique_types[0]

        return cls(BaseType.UNION, unique_types)
    
    @classmethod
    def callable(cls, arg_types: List['TypeInfo'], return_type: 'TypeInfo') -> 'TypeInfo':
        """Crée un type callable avec les types d'arguments et le type de retour."""
        args = cls(BaseType.ARGS, arg_types)
        return cls(BaseType.CALLABLE, [args, return_type])