// Implements a dictionary's functionality
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdbool.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

//number of buckets in hash table
const unsigned int N = 700;

//initialize number of words in dictionary
int word_count = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // Initializes index for hashed word
    int h = hash(word);
    // Sets cursor to point to same address as hashtable index/bucket
    node *cursor = table[h];
    // While cursor does not point to NULL, search dictionary for word.
    while (cursor != NULL)
    {
        // If strcasecmp returns true, then word has been found
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        // Else word has not yet been found, advance cursor
        else
        {
            cursor = cursor->next;
        }
    }
    // Cursor has reached end of list and word has not been found in dictionary so it must be misspelled
    return false;
}

// Hashes the word
// Hashing that will give you the index.
unsigned int hash(const char *word)
{
    unsigned int hash = 0;
    for (int i = 0, n = strlen(word); i < n; i++)
    {
        hash = hash + 69 * tolower(word[i]);
    }
    return hash % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Opens dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        return false;
    }
    // Scans dictionary word by word (populating hash table with nodes containing words found in dictionary)
    char word[LENGTH + 1];
    while (fscanf(file, "%s", word) != EOF)
    {
        // Mallocs a node for each new word (i.e., creates node pointers)
        node *new_node = malloc(sizeof(node));
        // Checks if malloc succeeded, returns false if not
        if (new_node == NULL)
        {
            fclose(file);
            unload();
            return false;
        }
        // Copies word into node if malloc succeeds
        strcpy(new_node->word, word);
        new_node->next = NULL;
        // Initializes & calculates index of word for insertion into hashtable
        int h = hash(word);

        // Inserts new nodes at beginning of lists
        if (table[h] == NULL)
        {
            table[h] = new_node;
            word_count++;
        }
        else
        {
            new_node->next = table[h];
            table[h] = new_node;
            word_count++;
        }
    }
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i < N; i ++)
    {
        while (table[i] != NULL)
        {
            node *tmp = table[i]->next;
            free(table[i]);
            table[i] = tmp;
        }
    }
    return true;
}
