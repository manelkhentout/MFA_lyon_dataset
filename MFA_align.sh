#!/bin/bash
#SBATCH --job-name=mfa-align
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=1
#SBATCH --time=1-00:00:00
#SBATCH --export=ALL
#SBATCH --output %x-%J.log
#SBATCH --mem=32G  # Increase as needed, e.g. 32GB


lyon="ur/path"
MFA="ur/path"

# initialise the forced-alignment environment
echo -e "Initialising the forced-alignment environment..."
#conda create -n MFA -c conda-forge montreal-forced-aligner=2.2.17
#conda activate MFA


# download the pretrained acoustic model, pronunciation dictionary and G2P model
echo -e "Downloading the pretrained acoustic model, pronunciation dictionary and G2P model..."
mfa model remove g2p french_mfa

mfa model download acoustic french_mfa
mfa model download dictionary french_mfa
mfa model download g2p french_mfa
echo -e "...done!"
mfa model inspect g2p french_mfa


# generate pronunciations for the OOV words and update the pretrained pronunciation dictionary with them
#echo -e "Updating the pretrained pronunciation dictionary with those of OOV words'...${NC}"
mfa g2p --clean  ${lyon} french_mfa ${MFA}/lyon_oov.txt --dictionary_path french_mfa
#echo -e "adding words to the dict..."

mfa model add_words french_mfa ${MFA}/lyon_oov.txt

#echo -e "start align..."
mfa align --clean -v ${lyon} french_mfa french_mfa ${lyon}/lyon_aligned
echo -e "end..."
