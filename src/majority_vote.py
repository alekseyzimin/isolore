import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--inp",default="jf_aligned.txt",help="Path to the jf alignment output")
    parser.add_argument("-o","--out",default=None,help="Path to the output file")
    parser.add_argument("-n","--neg",default=None,help="Path to the file containing the names of exons on the negative strand")
    args = parser.parse_args()
    
    neg_exons_list_file = open(args.neg,'r')
    neg_exons_list=neg_exons_list_file.read().splitlines()
    neg_exons_list_file.close()
    
    #majority voting and sorting by position of exon in the genome
    output_file=open(args.out, 'w')
    output_file.close()
    prev_read = "NaN"
    weight_dict={}
    exon_dict = {}
    lines_to_be_written=""
    read_counter = 0
    first_line= True
    with open(args.inp,'r') as f:
        for line in f:
            if first_line:
                first_line=False
                continue
            if line[0] == '>':
                if prev_read != "NaN":
                    lines_to_be_written,read_counter=write_exons(lines_to_be_written,read_counter,weight_dict,args.out,neg_exons_list,exon_dict,prev_read)
                    weight_dict={}
                    exon_dict = {}
                read_name=line.split()[-1]
                prev_read = read_name
           
            else: #alignments
                info = line.split()
                exon_name_and_pos=info[-1].split('_')
                exon_name='_'.join(exon_name_and_pos[0:2])
                exon_len = int(info[10])
                exon_seg_start_index = int(exon_name_and_pos[2])
                if exon_name not in weight_dict.keys():
                    weight_dict[exon_name] = 0
                    exon_dict[exon_name]=[]
            
           
                order ='+'
                matched_len = int(info[3])-int(info[2])+1
                exon_start = int(info[2])
                exon_end = int(info[3])
                read_start = int(info[0])
                read_end = int(info[1])
                if read_start > read_end:
                    temp=read_start
                    read_start = read_end
                    read_end=temp
                    order = '-'
                    overhang_added_read_start = read_start-(exon_len-exon_end) #1 based
                    overhang_added_read_end = read_end+exon_start-1
                else:
                    overhang_added_read_start = read_start-(exon_start-1)                                         
                    overhang_added_read_end = read_end+(exon_len-exon_end)  
                
            
                exon_dict[exon_name].append([order,exon_seg_start_index,"_".join(exon_name_and_pos),read_start,read_end,overhang_added_read_start,overhang_added_read_end,exon_len])
                weight_dict[exon_name]+= matched_len
                #matched_len_minus_errors = matched_len-int(info[8]) ask aleksey what to do
                #weight_dict[exon_name]+= matched_len_minus_errors
                
          
    read_counter = 9999  #write everything in the exon dict to file
    lines_to_be_written,read_counter=write_exons(lines_to_be_written,read_counter,weight_dict,args.out,neg_exons_list,exon_dict,prev_read)         
    return

def write_exons(lines_to_be_written,read_counter,weight_dict,out,neg_exons_list,exon_dict,read):
    if bool(weight_dict):
        best_exon=max(weight_dict, key=weight_dict.get)
        exon_data=exon_dict[best_exon]
        if len(exon_data) > 0:
           if (exon_data[0][0]=='+' and best_exon not in neg_exons_list) or (exon_data[0][0]=='-' and best_exon in neg_exons_list):
              exon_data.sort(key = lambda x: int(x[1]))
           else:
              exon_data.sort(key = lambda x: int(x[1]),reverse=True)

           lines_to_be_written += str('>'+read+'\n')
           n=0
           read_counter +=1
           for line in exon_data:
               n+=1
               lines_to_be_written += str('exon'+str(n)+' '+' '.join(str(item) for item in line[2:])+'\n')

    if read_counter == 10000:
        read_counter = 0
        with open(out, 'a') as of:
            of.write(lines_to_be_written)
            lines_to_be_written = ""
        
    return lines_to_be_written,read_counter

         
   
if __name__ == '__main__':
    main()
