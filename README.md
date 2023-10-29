# mass_rewriter
Extension for WEbUI

This is probably a little too complicated - but I build this to generate datasets, and use it all the time. It's most;ly for me to save here. Sure, you can mess with it, but I can't guarantee you will figure it out.

In anyway just to get a start - the text needs to be formatted with the \n\n\n between blocks of text (or whatever else you set in Block split) as it process it in block by block. and needs to reside in the input subfolder
To add blocks to a normal text, you can use the Blockify tab - it will create whatever.blockify.txt file in the input and se[arate blocks of text roughly by the number of characters specified. then you can use the .blockify.txt as your input.
it uses LLM to format the text blocks to what you need - but you need to have smart model that does what you want it to do. 
So usually the first step is to train a helper model that can be then used as the source model for reformatting/rewritting text.
One of them for example my : https://huggingface.co/FPHam/Reverso_13b_Q_Generator_GPTQ
That has been used exactly with this to create datasets that start with a question.
