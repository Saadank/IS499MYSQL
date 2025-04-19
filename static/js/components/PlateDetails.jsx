import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 20px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, auto);
  gap: 1rem;
  margin: 2rem 0;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(4, auto);
  }
`;

const GridItem = styled.div`
  background: #f5f5f5;
  padding: 15px;
  text-align: center;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
`;

const Label = styled.div`
  color: #666;
  margin-bottom: 5px;
  font-size: 0.9rem;
`;

const Value = styled.div`
  color: #333;
  font-weight: 500;
  font-size: 1rem;
`;

const LoginNotice = styled.div`
  text-align: center;
  padding: 12px;
  margin-top: 2rem;
  color: #666;
`;

const PlateDetails = ({ plate, username }) => {
  if (!plate) {
    return (
      <Container>
        <div>No plate found</div>
      </Container>
    );
  }

  const details = [
    { label: 'Ad #', value: plate.plateID },
    { label: 'Plate Number', value: plate.plate_number },
    { label: 'Country', value: 'K S A' },
    { label: 'City', value: plate.city },
    { label: 'Publication Date', value: new Date(plate.created_at).toLocaleDateString() },
    { label: 'Price', value: `SAR ${plate.price.toFixed(2)}` },
    { label: 'Transfer Cost', value: plate.transfer_cost },
    { label: 'Plate Type', value: plate.plate_type }
  ];

  return (
    <Container>
      <Grid>
        {details.map((detail, index) => (
          <GridItem key={index}>
            <Label>{detail.label}</Label>
            <Value>{detail.value}</Value>
          </GridItem>
        ))}
      </Grid>
      
      {!username && (
        <LoginNotice>
          Please login to contact the seller
        </LoginNotice>
      )}
    </Container>
  );
};

export default PlateDetails; 